# MM - 2024.05.04.
# Modulzáró project
# Könyv kölcsönző alkalmazás

from flask import Flask, render_template, request, redirect, url_for
import json
from random import randint
from datetime import date
from admin import BookSearchAppAdmin
from selenium_test import SeleniumTest
import threading

class BookSearchApp:
    def __init__(self):
        self.app = Flask(__name__, template_folder='templates', static_url_path='/static')
        self.load_books_data()
        self.selected_books = {}

    def load_books_data(self):
        with open('konyv.json', 'r', encoding='utf-8') as f:
            self.books_data = json.load(f)['books']

    def run(self):
        self.register_admin_routes()
        self.register_routes()
        self.app.run(debug=True, port=5001)

    def register_routes(self):
        self.app.add_url_rule('/', 'index', self.index, methods=['GET', 'POST'])
        self.app.add_url_rule('/search', 'search', self.search, methods=['POST'])
        self.app.add_url_rule('/process_selection', 'process_selection', self.process_selection, methods=['POST'])
        self.app.add_url_rule('/rent_confirmation', 'rent_confirmation', self.rent_confirmation, methods=['GET', 'POST'])
        self.app.add_url_rule('/return_book', 'return_book', self.return_book, methods=['GET', 'POST'])
        self.app.add_url_rule('/return_confirmation', 'return_confirmation', self.return_confirmation, methods=['GET', 'POST'])

    def register_admin_routes(self):
        Admin = BookSearchAppAdmin()
        self.app.add_url_rule('/admin_login', 'admin_login', Admin.admin_login, methods=['GET', 'POST'])
        self.app.add_url_rule('/admin_page', 'admin_page', Admin.admin_page, methods=['GET', 'POST'])
        self.app.add_url_rule('/admin_search', 'admin_search', Admin.search, methods=['POST'])
        self.app.add_url_rule('/edit_book_data', 'edit_book_data', Admin.edit_book_data, methods=['GET', 'POST'])
        self.app.add_url_rule('/add_book_data', 'add_book_data', Admin.add_book_data, methods=['GET', 'POST'])
        self.app.add_url_rule('/run_test', 'run_test', self.run_test, methods=['POST'])

    def index(self):
        warning = False
        if request.method == 'POST':
            self.update_rental_history()
            warning = "The rent was successful."
        elif request.method == 'GET':
            if request.args:
                self.update_return_history()
                warning = "The return was successful."
        return render_template('index.html', books={}, selected_books=self.selected_books, warning=warning)

    def search(self):
        search_term = request.form['searchInput']
        search_by = request.form['searchSelect']
        filtered_books = self.filter_books(search_term, search_by)

        if not filtered_books:
            warning_message = "Unfortunately, there are no books matching the search criteria or" \
                              " there may be a typo in the search term. Please try again with different search parameters."
            return render_template('index.html', books={}, warning=warning_message, selected_books=self.selected_books)

        return render_template('index.html', books=filtered_books, selected_books=self.selected_books)

    def filter_books(self, search_term, search_by):
        filtered_books = {}
        try:
            if search_by == "ISBN":
                for isbn, book in self.books_data.items():
                    if isbn == search_term:
                        filtered_books[isbn] = book
            elif search_by == "page_count":
                for isbn, book in self.books_data.items():
                    search_selection = book.get(search_by)
                    if int(search_term) >= int(search_selection):
                        filtered_books[isbn] = book
            elif search_by == "languages":
                for isbn, book in self.books_data.items():
                    search_selection = book.get(search_by)
                    for language in search_selection:
                        if language.lower() == search_term.lower():
                            filtered_books[isbn] = book
            else:
                for isbn, book in self.books_data.items():
                    search_selection = book.get(search_by)
                    if search_term.lower() in search_selection.lower():
                        filtered_books[isbn] = book
        except ValueError:
            pass
        return filtered_books

    def process_selection(self):
        selected_isbns = request.form.getlist("selected_books[]")
        for isbn in selected_isbns:
            single_book_data = self.books_data.get(isbn)
            if single_book_data not in self.selected_books.values():
                self.selected_books[isbn] = single_book_data

        return render_template('index.html', selected_books=self.selected_books)

    def is_rental_number_used(self, number):
        for isbn, book in self.books_data.items():
            rental_history = book.get('rental_history', [])
            if rental_history:
                last_rental_entry = rental_history[-1]
                user_id_element = last_rental_entry['user_id'][1]
                if number == user_id_element:
                    return True
        return False

    def rent_confirmation(self):
        generated_number = None
        while generated_number is None or self.is_rental_number_used(generated_number):
            generated_number = '{:05d}'.format(randint(1, 99999))
        return render_template('confirmation.html', selected_books=self.selected_books, user_number=generated_number)

    def update_rental_history(self):
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        user_number = request.form.get("userNumber")
        for selected_isbn, selected_book in self.selected_books.items():
            for all_isbn, all_book in self.books_data.items():
                if selected_isbn == all_isbn:
                    all_book['rental_history'].append({
                    'user_id': [f"{first_name.capitalize()} {last_name.capitalize()}", int(user_number)],
                    'rental_date': str(date.today()),
                    'return_date': None
                })
                    all_book["availability"] = "rented"
        self.selected_books = {}
        with open('konyv.json', 'w', encoding="utf-8") as f:
            json.dump({'books': self.books_data}, f, indent=5, ensure_ascii=True)

    def return_confirmation(self):
        return_books = {}
        first_name = request.form.get('firstName', '').strip().capitalize()
        last_name = request.form.get('lastName', '').strip().capitalize()
        user_number = request.form.get('userNumber', '').strip()

        if not first_name and not last_name and not user_number:
            return render_template('return_book.html', confirm=False, message="Please provide either your name or rent number.")

        try:
            user_number = int(user_number) if user_number else 0
        except ValueError:
            user_number = 0

        end_name = f"{first_name} {last_name}"
        if first_name and last_name or user_number != 0:
            for isbn, book in self.books_data.items():
                rental_history = book.get("rental_history", [])
                if rental_history and book['availability'] != "available":
                    last_rental_entry = rental_history[-1]
                    user_id = last_rental_entry["user_id"]
                    full_name = user_id[0]
                    rent_number = int(user_id[-1])

                    if (first_name and last_name and full_name == f"{first_name} {last_name}") or (user_number == rent_number):
                        end_name = user_id[0]
                        return_books[isbn] = book

            if not return_books:
                return render_template('return_book.html', confirm=False, message="No matching rental records found.")
        else:
            return render_template('return_book.html', confirm=False,
                                   message="Please provide either your full name or rent number.")

        return render_template('return_book.html', confirm=True, books=return_books, user_info=end_name)

    def update_return_history(self):
        selected_isbns = request.args.getlist("selected_books[]")
        for isbn in selected_isbns:
            self.books_data[isbn]["availability"] = "available"
            self.books_data[isbn]["rental_history"][-1]["return_date"] = str(date.today())
        self.selected_books = {}
        with open('konyv.json', 'w', encoding="utf-8") as f:
            json.dump({'books': self.books_data}, f, indent=5, ensure_ascii=True)


    def return_book(self):
        return render_template('return_book.html', confirm=False)

    def run_test(self):
        def run_selenium_test():
            test = SeleniumTest("http://127.0.0.1:5001/")
            test.run_test()
        threading.Thread(target=run_selenium_test).start()
        return render_template('index.html', books={}, selected_books=self.selected_books, warning="The selenium test started for more information check app.log in the main folder")

if __name__ == '__main__':
    app = BookSearchApp()
    app.run()