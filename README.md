<div align="right">
  <a href="https://nbd.wtf">
    <img height="196" src="https://user-images.githubusercontent.com/1653275/194609043-0add674b-dd40-41ed-986c-ab4a2e053092.png" />
  </a>
</div>

## emeralize

----

emeralize is a Lightning-enabled marketplace (ecommerce) and Learning Management System (LMS) that has the ability to enable learn-to-earn on free and paid content.

## Features

- Learning Management System
- Content Management System
- Marketplace
- Wallet & Transaction System
- Paywall
- Value-4-Value (V4V) Content
- Tipping
- Payment Splitting (courses and ebooks)
- Bitcoin Lightning Payments
- Automatic Withdrawals to Lightning Address

## About the Codebase

emeralize is built on the [django web framework](https://djangoproject.com).

It has a few main apps:
- emeralize. This is the project settings. Check `emeralize/settings.py``.
- Accounts. Which deals with authentication things such as registration, login, reset password, and more.
- Criticalpath. This is the main learning management system app.
- Marketplace. This is where the ecommerce, wallet, and transactional features live.
- Everything else is just for files and some one off template for auth. I know it's bad but I haven't had time to refactor it.

## Use Cases

- Blogs
- Ecommerce
- Learning Management System

## env Variables

Rename the `.env.example` file to `.env` and fill out the required settings.

## Setting up a Local Environment

First ensure that you have [python](https://python.org) installed. if not, install it.

Clone the repo.
`git clone https://github.com/nbd-wtf/emeralize.git`

Create a new virtual environment:
`python3 -m venv env`

Activate the environment:
`source env/bin/activate`

Navigate to the `app` directory, then install the requirements.txt.

`cd app && pip3 install -r requirements.txt`

OK, now you have the requirements. Let's make migrations and execute the migration. This will build all the tables from your database. This is viewable for each app in the m odels.py files in their respective directories.

`python3 manage.py makemigrations && python3 manage.py migrate`

boom.

Now, let's create a super user. Part of the nice thing about django is you get a free admin panel.

`python3 manage.py createsuperuser`

Fill out the prompts for your information. Once you have the super user created, go ahead and run the server.
`python3 manage.py runserver`

Now, let's go to our admin panel.
https://localhost:8000/admin/

## Setting up the Database

### Transaction Types
Create a transaction type with the type Debit **FIRST**. This will be 0.
Create a transaction type with the type Credit **SECOND**. This will be 1.

### Transaction Codes

#### Debits
Create the following named EXACTLY as they appear.
Assign each with transaction type 0:
- `Split Payout`
- `Withdrawal`
  
#### Credits
Create the following named EXACTLY as they appear.
Assign each with transaction type 1:

- `Workshop Purchase`
- `Ebook Purchase`
- `Split Payment`
- `Resource Reward`
- `Course Purchase`
- `Resource Purchase`
- `Tip`

## Deployment.
You're now all set to use emeralize locally. You can follow this guide to see how to deploy the app to [namecheap](https://www.youtube.com/watch?v=nvq7NNSfKdw). If there's interest I can write a guide for AWS deployment.