# MM - 2024.06.02.
# Modulzáró project
# Könyv kölcsönző alkalmazás (admin felhasználó)

import os
from dotenv import load_dotenv
from flask import render_template, request
import json
import pandas as pd
from selenium_test import SeleniumTest


class BookSearchAppAdmin:
    load_dotenv("admin.env")

    def __init__(self):
        self.first_name = os.getenv('ADMIN_FIRST_NAME')
        self.last_name = os.getenv('ADMIN_LAST_NAME')
        self.admin_num = os.getenv('ADMIN_NUM')
        self.massage = 0
        self.book_to_add = {}

    def load_books_data(self):
        # Load data from konyv.json into self.books_df DataFrame
        with open('konyv.json', 'r', encoding='utf-8') as f:
            data_dict = json.load(f)['books']
        books_list = []
        for isbn, book in data_dict.items():
            book_data = {
                'isbn': isbn,
                'title': book['title'],
                'author': book['author'],
                'author_nationality': book['author_nationality'],
                'year_written': book['year_written'],
                'page_count': book['page_count'],
                'category': book['category'],
                'languages': book['languages'],  # Assuming it's already a list
                'availability': book['availability'],
                'rental_history': book['rental_history']  # Use directly assuming it's already a list
            }
            books_list.append(book_data)
        self.books_df = pd.DataFrame(books_list)

    def df_to_dict(self, df):
        result = {}
        for _, row in df.iterrows():
            result[row['isbn']] = {
                'title': row['title'],
                'author': row['author'],
                'author_nationality': row['author_nationality'],
                'year_written': row['year_written'],
                'page_count': row['page_count'],
                'category': row['category'],
                'languages': row['languages'],
                'availability': row['availability'],
                'rental_history': row['rental_history']
            }
        return result

    def authenticate(self, first_name, last_name, admin_num):
        return (self.first_name == first_name and
                self.last_name == last_name and
                self.admin_num == str(admin_num))

    def admin_login(self):
        if request.method == 'POST':
            action = request.form.get('function')
            if action == 'Delete':
                self.delete_data()
        return render_template('admin_login.html')

    def admin_page(self):
        first_name_log = request.form.get("firstName")
        last_name_log = request.form.get("lastName")
        admin_number_log = request.form.get("adminNumber")
        self.full_name = f"{first_name_log} {last_name_log}"
        if self.authenticate(first_name_log, last_name_log, admin_number_log):
            match self.massage:
                case 0:
                    self.load_books_data()
                    return render_template('admin_page.html', admin_full_name=self.full_name,
                                           books=self.df_to_dict(self.books_df))
                case 1:
                    self.add_data_to_database()
                    self.load_books_data()
                    return render_template('admin_page.html', admin_full_name=self.full_name,
                                           books=self.df_to_dict(self.books_df),
                                           warning="A new book has been successfully added to the database.")
                case 2:
                    self.update_edited_data_in_database()
                    self.load_books_data()
                    return render_template('admin_page.html', admin_full_name=self.full_name,
                                           books=self.df_to_dict(self.books_df),
                                           warning="The book data has been successfully edited in the database.")
                case 3:
                    self.load_books_data()
                    self.massage = 0
                    return render_template('admin_page.html', admin_full_name=self.full_name,
                                           books=self.df_to_dict(self.books_df),
                                           warning="The selected books have been successfully deleted from the database.")
        else:
            return render_template('index.html', books={}, selected_books={},
                                   warning="Authentication failed: please check your first name, last name, and admin number.")

    def edit_book_data(self):
        if request.method == "GET":
            selected_books = request.args.getlist("selected_books[]")
            selected_books_df = self.books_df[self.books_df['isbn'].isin(selected_books)]
            self.selected_books_dict = self.df_to_dict(selected_books_df)
            return render_template('edit_book_data.html', selected_books=self.selected_books_dict,
                                   admin_full_name=self.full_name)
        else:
            self.edit_data_in_database()
            return render_template('edit_book_data.html', selected_books=self.books_edited,
                                   admin_full_name=self.full_name, warning="The edit was made to finish and update the database use the 'Finish' button")

    def search(self):
        search_term = request.form['searchInput']
        search_by = request.form['searchSelect']
        filtered_books = self.df_to_dict(self.filtered_df(search_by, search_term))
        if not filtered_books:
            warning_message = "Unfortunately, there are no books matching the search criteria or" \
                              " there may be a typo in the search term. Please try again with different search parameters."
            return render_template('admin_page.html', books=self.df_to_dict(self.books_df), warning=warning_message, admin_full_name=self.full_name)

        return render_template('admin_page.html', books=filtered_books, warning="Search Success", admin_full_name=self.full_name)

    def filtered_df(self, search_b, search_t):
        book_by_search = self.books_df[self.books_df[search_b] == search_t]
        return book_by_search

    def add_book_data(self):
        if request.method == 'POST':
            self.add_single_file()
            return render_template('add_book_data.html', admin_full_name=self.full_name,
                                   warning="The book has been added successfully. Please use the 'Finish' button to complete the process.")
        return render_template('add_book_data.html', admin_full_name=self.full_name)

    def add_single_file(self):
        languages_raw = request.form['languages']
        self.book_to_add[len(self.book_to_add)] = {
        'isbn': request.form['isbn'],
        'title': request.form['title'],
        'author': request.form['author'],
        'author_nationality': request.form['author_nationality'],
        'year_written': int(request.form['year_written']),
        'page_count': int(request.form['page_count']),
        'category': request.form['category'],
        'languages': languages_raw.strip().split(','),
        'availability': "available",
        'rental_history': []
    }
        self.massage = 1

    def add_data_to_database(self):
        for _, book in self.book_to_add.items():
            new_book_df = pd.DataFrame([book])
            self.books_df = pd.concat([self.books_df, new_book_df], ignore_index=True)
        file_to_upload = self.df_to_dict(self.books_df)
        with open('konyv.json', 'w', encoding="utf-8") as f:
            json.dump({'books': file_to_upload}, f, indent=5, ensure_ascii=True)
        self.massage = 0

    def edit_data_in_database(self):
        self.books_edited = {}
        isbn_list = request.form.getlist("isbn[]")
        title_list = request.form.getlist("title[]")
        author_list = request.form.getlist("author[]")
        author_nationality_list = request.form.getlist("author_nationality[]")
        year_written_list = request.form.getlist("year_written[]")
        page_count_list = request.form.getlist("page_count[]")
        category_list = request.form.getlist("category[]")
        languages_list = request.form.getlist("languages[]")
        availability_list = request.form.getlist("availability[]")
        rent_name_lists = request.form.getlist("rent_name[]")
        rent_number_lists = request.form.getlist("rent_number[]")
        rent_date_lists = request.form.getlist("rent_date[]")
        return_date_lists = request.form.getlist("return_date[]")

        for i in range(len(isbn_list)):
            isbn = isbn_list[i]
            title = title_list[i]
            author = author_list[i]
            nationality = author_nationality_list[i]
            year = year_written_list[i]
            pages = page_count_list[i]
            category = category_list[i]
            languages = languages_list[i]
            availability = availability_list[i]

            # Split languages by comma and strip spaces
            languages = [lang.strip() for lang in languages.split(',')]

            # Create rental history for the current book
            rent_history = []
            book_df_foredit = self.books_df[self.books_df["isbn"] == isbn]
            num_of_rentals = book_df_foredit['rental_history'].apply(len).iloc[0]


            for j in range(num_of_rentals):
                rent_history.append({
                    "user_id": [rent_name_lists.pop(0), int(rent_number_lists.pop(0))],
                    "rental_date": rent_date_lists.pop(0),
                    "return_date": return_date_lists.pop(0)
                })

            # Update books_edited dictionary with the current book's data
            self.books_edited[isbn] = {
                'title': title,
                'author': author,
                'author_nationality': nationality,
                'year_written': int(year),
                'page_count': int(pages),
                'category': category,
                'languages': languages,
                'availability': availability,
                'rental_history': rent_history
            }
        self.massage = 2

    def update_edited_data_in_database(self):
        books_to_upload = {}
        book_data_dict = self.df_to_dict(self.books_df)
        for isbn, book in book_data_dict.items():
            for isbn_edit, book_edit in self.books_edited.items():
                if isbn == isbn_edit:
                    books_to_upload[isbn_edit] = {
                        'title': book_edit["title"],
                        'author': book_edit["author"],
                        'author_nationality': book_edit["author_nationality"],
                        'year_written': int(book_edit["year_written"]),
                        'page_count': int(book_edit["page_count"]),
                        'category': book_edit["category"],
                        'languages': book_edit["languages"],
                        'availability': book_edit["availability"],
                        'rental_history': book_edit["rental_history"]
                    }
                else:
                    books_to_upload[isbn] = {
                        'title': book["title"],
                        'author': book["author"],
                        'author_nationality': book["author_nationality"],
                        'year_written': int(book["year_written"]),
                        'page_count': int(book["page_count"]),
                        'category': book["category"],
                        'languages': book["languages"],
                        'availability': book["availability"],
                        'rental_history': book["rental_history"]
                    }

        # Save to konyv.json ensuring rental_history and languages remain in the correct format
        with open('konyv.json', 'w', encoding="utf-8") as f:
            json.dump({'books': books_to_upload}, f, indent=5, ensure_ascii=True)
        self.message = 2

    def delete_data(self):
        # Get the selected books from the form
        selected_books = request.form.get("isbn")
        # Remove the selected books from the DataFrame
        self.books_df = self.books_df[self.books_df['isbn'] != selected_books]
        # Update the JSON file
        books_to_upload = self.df_to_dict(self.books_df)
        with open('konyv.json', 'w', encoding='utf-8') as f:
            json.dump({'books': books_to_upload}, f, indent=5, ensure_ascii=True)
        self.massage = 3

