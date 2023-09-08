from marketplace.config import API_KEY, CALLBACK_URL
from django.contrib.auth.models import User
from marketplace.models import *
from criticalpath.models import *

import requests, json
import math

def get_platform_fee(amount):
    if amount * .02 <= 1:
        fee = 1
    else:
        fee = amount * .02
    return math.floor(fee)

def get_usd_exchange_rate():
    URL = 'https://api.zebedee.io/v0/btcusd'
    heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
    usd_price = requests.get(URL, headers=heads).json()["data"]["btcUsdPrice"]
    return int(usd_price)

def check_if_usd(creation):
    pass

def calc_usd_to_sats(usd_amount, bitcoin_price):
    SATS_PER_BITCOIN = 100000000
    amount_of_bitcoin = usd_amount / bitcoin_price
    sats_amount = SATS_PER_BITCOIN * amount_of_bitcoin
    return math.floor(sats_amount)

def calc_sats_to_msats(sat_amount):
    return str(sat_amount) + "000"

def get_currency(currency_id):
    return Currency.objects.get(id=currency_id)

def get_msat_amount(price, currency_id):
    currency = get_currency(currency_id)
    if currency.iso_code == "SAT":
        msats_amount = calc_sats_to_msats(price)
        return msats_amount
    elif currency.iso_code == "USD":
        bitcoin_price = get_usd_exchange_rate()
        sats_amount_from_usd = calc_usd_to_sats(price, bitcoin_price)
        msats_amount = calc_sats_to_msats(sats_amount_from_usd)
        return msats_amount
    
def get_sat_amount(price, currency_id):
    currency = get_currency(currency_id)
    if currency.iso_code == "SAT":
        return price
    elif currency.iso_code == "USD":
        bitcoin_price = get_usd_exchange_rate()
        sats_amount_from_usd = calc_usd_to_sats(price, bitcoin_price)
        return sats_amount_from_usd

def calc_payout_amount(amount):
    return amount - get_platform_fee(amount)

def user_eligible_for_withdrawal(user_balance):
    if user_balance >= 10:
        return True
    return False 

def check_wallet_lock_status(user):
    user_wallet = Wallet.objects.get(user=user) 
    if user_wallet.is_locked:
        return True
    return False

def lock_user_wallet(user):
    update_lock_status = {"is_locked" : True}
    Wallet.objects.filter(user=user).update(**update_lock_status)
    return True

def unlock_user_wallet(user):
    update_lock_status = {"is_locked" : False}
    Wallet.objects.filter(user=user).update(**update_lock_status)
    return True

def create_charge(charge_type, user, id, description, amount):
    # params: charge_type, id, description, user
    metadata = {}

    if charge_type == "resource_purchase":
        metadata = f"resource:{id}"
    elif charge_type == "creator_tip":
        metadata = f"tip_receiver:{id}"

    elif charge_type == "course_purchase":
        metadata = f"course:{id}"

    elif charge_type == "ebook_purchase":
        metadata = f"ebook:{id}"
    elif charge_type == "workshop_purchase":
        metadata = f"workshop:{id}"


    URL = 'https://api.zebedee.io/v0/charges'
    heads = {'Content-Type': 'application/json', 'apikey': API_KEY}


    charge_data = json.dumps({
        "expiresIn": 600,
        "amount": str(amount),
        "description": description,
        "internalId": metadata,
        "callbackUrl": CALLBACK_URL
    })
    print(charge_data)


    response = requests.post(URL, headers=heads, data=charge_data).json()

    ln_data = response["data"]
    if user is not None:
        charge = Charge.objects.create(
                            user=user,
                            description=ln_data["description"],
                            amount=int(ln_data["amount"]) / 1000,
                            status=ln_data["status"],
                            unit = "sats",
                            external_id=ln_data["id"],
                            internal_id=ln_data["internalId"],
                            callback_url=ln_data["callbackUrl"],
                            charge_encoded=ln_data["invoice"]["request"],
                            uri = ln_data["invoice"]["uri"],
                            expires_at=ln_data["expiresAt"],
                            created_at=ln_data["createdAt"]
                            ).save()
    else:
        charge = Charge.objects.create(
                            description=ln_data["description"],
                            amount=int(ln_data["amount"]) / 1000,
                            status=ln_data["status"],
                            unit = "sats",
                            external_id=ln_data["id"],
                            internal_id=ln_data["internalId"],
                            callback_url=ln_data["callbackUrl"],
                            charge_encoded=ln_data["invoice"]["request"],
                            uri = ln_data["invoice"]["uri"],
                            expires_at=ln_data["expiresAt"],
                            created_at=ln_data["createdAt"]
                            ).save()

    return ln_data

def update_charge(charge):
    update_data = {
        "status": charge["data"]["status"]
    }
    Charge.objects.filter(external_id=charge["data"]["id"]).update(**update_data)
    c = Charge.objects.get(external_id=charge["data"]["id"])
    return c

def create_purchase(**kwargs):
    # conditionals to determine if resource and creator
    if resource:
        p_data = {
            "charge" : c,
            "user" : c.user,
            "resource" : resource
        }
    elif course:
        p_data = {
            "charge" : c,
            "user" : c.user,
            "course" : co,
        }
    Purchase.objects.create(**p_data)
    return True

def update_credit_status(charge):
    update_credit_status = {
        "user_credited" : True
    }
    Charge.objects.filter(external_id=charge.id).update(**update_credit_status)    
    return True

def get_payment_split_config(split_type, creation_obj):
    if split_type == "course":
        payment_splits = CoursePaymentSplits.objects.filter(course=creation_obj)
    elif split_type == "ebook":
        payment_splits = EbookPaymentSplits.objects.filter(ebook=creation_obj)
    elif split_type == "workshop":
        payment_splits = WorkshopPaymentSplits.objects.filter(workshop=creation_obj)   
    return payment_splits

def execute_single_payout(comment, creator):
    #user, amount, comment

    print("Single Payout Executed.")

    # need to calc amount, min of 1 sat for a fee

    #pay out to ln address automatically

    # get user profile to see if they have an ln address
    creator_profile = get_user_profile(creator)
    # check if user has an ln address
    if creator_profile.lightning_address is not None:
        creator_wallet = get_user_wallet(creator)
        print(creator_wallet.balance)
        print("Fetched Creator Wallet for Automatic Withdrawal")
        # payout only if >= 100 sats
        if check_automatic_withdrawal_eligibility(creator_wallet):
            print("Withdrawal Eligible")
            # check if ln address is valid
            if lightning_address_is_valid(creator_profile.lightning_address):
                print("Lightning Address Valid")
                payment = send_payment_to_lightning_address(creator_profile.lightning_address, str(creator_wallet.balance) + "000", comment)
                print(payment)
                # since ln address is async now, we may need to add this step to the callback.
                if payment is True:
                    execute_transactions(creator, creator_wallet.balance, None, "withdrawal", None)
                    # example: execute_transactions(user, amount, charge, transaction_type, creation_obj)
                    update_wallet_balance(creator, 0)
                    print("Payment Successful. Executed withdrawal Transactions.")
                    return True
                else:
                    # if the payment fails show error message
                    return payment

def create_purchases(creation_obj, charge, purchase_type):
    if not charge.user_credited:

        if purchase_type == "course":
            purchase = Purchase.objects.all().filter(course=creation_obj, user=charge.user)
            #prevents double credit.
            # Credit purchases


            # grant a purchase to the purchaser
            t_data = {
                "charge" : charge,
                "user" : charge.user,
                "course" : creation_obj,
            }

            Purchase.objects.create(**t_data)

            create_purchases(creation_obj, charge, "course_resources")
        elif purchase_type == "course_resources":
            course_resources = CourseResources.objects.all().filter(course=creation_obj)


            pr_code = TransactionCode.objects.get(transaction_code_text="Resource Purchase")
            for course_resource in course_resources:
                check_if_purchase_exists = Purchase.objects.all().filter(user=charge.user, resource=course_resource.resource)
                if not check_if_purchase_exists:
                    prt_data = {
                        "charge" : charge,
                        "user" : charge.user,
                        "resource" : course_resource.resource
                    }
                    Purchase.objects.create(**prt_data)


                else:
                    continue
        elif purchase_type == "resource":
            p_data = {
                "charge" : charge,
                "user" : charge.user,
                "resource" : creation_obj
            }
            Purchase.objects.create(**p_data)


        elif purchase_type == "workshop":
            p_data = {
                "charge" : charge,
                "user" : charge.user,
                "workshop" : creation_obj
            }
            Purchase.objects.create(**p_data)

        elif purchase_type == "workshop":
            p_data = {
                "charge" : charge,
                "user" : charge.user,
                "workshop" : creation_obj
            }
            Purchase.objects.create(**p_data)

def execute_transactions(user, amount, charge, transaction_type, creation_obj):

    if transaction_type == "course":
        t_code = TransactionCode.objects.get(transaction_code_text="Course Purchase")
        transaction = Transaction.objects.create(
                            description=f"{charge.user} purchased {creation_obj.title} for {amount} sats from {creation_obj.creator}",
                            user=user,
                            amount=amount,
                            transaction_code=t_code
                            ).save()
        
        print("Course transaction executed.")
        course_resources = CourseResources.objects.all().filter(course=creation_obj)
        for course_resource in course_resources:
            execute_transactions(charge.user, 0, None, "course_resource", course_resource)
    elif transaction_type == "payout":
        t_code = TransactionCode.objects.get(transaction_code_text="Split Payout")
        transaction = Transaction.objects.create(
                            description=f"Split payout for {amount} sats to {user} from {creation_obj.title} Purchase.",
                            user=creation_obj.creator,
                            amount=amount,
                            transaction_code=t_code
                            ).save()
        print("Payout transaction for creator executed.")
    elif transaction_type == "split_payment":
        t_code = TransactionCode.objects.get(transaction_code_text="Split Payment")
        transaction = Transaction.objects.create(
                            description=f"Payment to {user} for {amount} sats from purchased {creation_obj.title} split.",
                            user=user,
                            amount=amount,
                            transaction_code=t_code
                            ).save()
    elif transaction_type == "withdrawal":
        t_code = TransactionCode.objects.get(transaction_code_text="Withdrawal")
        transaction = Transaction.objects.create(
                            description=f"Automatic Withdrawal for {amount} sats from emeralize",
                            user=user,
                            amount=amount,
                            transaction_code=t_code
                            ).save()
    elif transaction_type == "tip":
        t_code = TransactionCode.objects.get(transaction_code_text="Tip")
        Transaction.objects.create(
                            description=f"{charge.description}",
                            user=user,
                            amount=amount,
                            transaction_code=t_code
                            ).save()
    elif transaction_type == "resource":
        t_code = TransactionCode.objects.get(transaction_code_text="Resource Purchase")
        Transaction.objects.create(
                            description=f"{charge.description}",
                            user=user,
                            amount=amount,
                            transaction_code=t_code
                            ).save()
    elif transaction_type == "course_resource":
        t_code = TransactionCode.objects.get(transaction_code_text="Resource Purchase")

        Transaction.objects.create(
            description=f"{user} purchased {creation_obj.resource.title} via {creation_obj.resource.title} from {creation_obj.resource.creator}",
            user=creation_obj.resource.creator,
            amount=amount,
            transaction_code=t_code
            ).save()                 
    elif transaction_type == "ebook":
        t_code = TransactionCode.objects.get(transaction_code_text="Ebook Purchase")
        Transaction.objects.create(
                            description=f"{charge.description}",
                            user=user,
                            amount=amount,
                            transaction_code=t_code
                            ).save()
        
    elif transaction_type == "workshop":
        t_code = TransactionCode.objects.get(transaction_code_text="Workshop Purchase")
        Transaction.objects.create(
                            description=f"{charge.description}",
                            user=user,
                            amount=amount,
                            transaction_code=t_code
                            ).save()
    
def update_credit_status(charge):
    update_credit_status = {
            "user_credited" : True
        }
    return Charge.objects.filter(external_id=charge).update(**update_credit_status)   

def execute_wallet_adjustments(user, amount, charge):
    # credit the course creator
    # this saves us from having to do it in multiple steps / repeat ourselves. we'll do another
    # tx if the withdrawal is successful to have the full history.
    
    creator_wallet = get_user_wallet(user)
    new_balance = creator_wallet.balance + amount
    update_wallet_balance(user, new_balance)
    if charge is not None:
        update_credit_status(charge)

def get_user_profile(user):
    return UserProfile.objects.get(user=user)

def get_user_wallet(user):
    return Wallet.objects.get(user=user)

def check_automatic_withdrawal_eligibility(wallet):
    return wallet.balance >= 100

def lightning_address_is_valid(lightning_address):
    url = f'https://api.zebedee.io/v0/ln-address/validate/{lightning_address}'
    heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
    response = requests.get(url, headers=heads).json()

    # if it is a valid ln address
    if response["data"]["valid"]:
        return True
    else:
        return False
    
def update_wallet_balance(user, amount):
    wallet = get_user_wallet(user)
    update_balance_data = {
        "balance": amount,
    }
    Wallet.objects.filter(user=user).update(**update_balance_data)    
    return True  

def send_payment_to_lightning_address(lightning_address, amount, comment, transaction_id = None):
    URL = 'https://api.zebedee.io/v0/ln-address/send-payment'
    heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
    lnadrs_payment_payload = json.dumps({
        "lnAddress": f"{lightning_address}",
        "amount": f"{amount}",
        "comment": f"{comment}",
        # no callback just yet. I will add support for a lightning address tx overtime to maintain auditability and statuses for users.
        # "callbackUrl" : CALLBACK_URL,
        "internalId" : f"withdrawal:{transaction_id}"
    })


    response = requests.post(URL, headers=heads, data=lnadrs_payment_payload).json()
    if response["success"]:
        # unlock_user_wallet(user)
        return response["success"]
    else:
        # unlock_user_wallet(user)
        return response["message"]
    # check if the payment was successful and update balance to 0 if it was

def execute_payment_splits(payment_splits, payout_amount, creation_obj):

    for ps in payment_splits:
            print(ps)
            # Get the payout amount. Already taken fee upfront. 
            ps_payout = math.floor(payout_amount * (ps.amount/100))

            # 1- execute split payout transaction
            execute_transactions(creation_obj.creator, ps_payout, None, "payout", creation_obj)

            # 2- Subtracting payout from course owner.
            creation_owner_wallet = get_user_wallet(creation_obj.creator)
            creation_owner_current_balance = creation_owner_wallet.balance
            creation_owner_new_balance = creation_owner_current_balance - ps_payout
            update_wallet_balance(creation_obj.creator, creation_owner_new_balance)

            # 3- execute split payment transaction
            execute_transactions(ps.user, ps_payout, None, "split_payment", creation_obj)
            
            # credit the course creator
            # this saves us from having to do it in multiple steps / repeat ourselves. we'll do another
            # tx if the withdrawal is successful to have the full history.

            # 4- Crediting payment to split user.
            creator_wallet = Wallet.objects.get(user=ps.user)
            new_balance = creator_wallet.balance + ps_payout
            update_wallet_balance(ps.user, new_balance)


            # 5- Execute Single Payout
            execute_single_payout("Automatic Withdrawal to Lightning Address from emeralize", ps.user)