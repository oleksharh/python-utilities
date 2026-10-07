import csv
import json

GOOGLE_CONTACT_HEADERS = [
    "First Name",
    "Last Name",
    "Labels",
    "Phone 1 - Label",
    "Phone 1 - Value",
]


def load_telegram_contacts(path: str, encoding: str = "utf-8") -> list[dict[str, str]]:
    with open(path, "r", encoding=encoding) as json_file:
        data = json.load(json_file)
        contacts = data["contacts"][
            "list"
        ]  # everything else is metadata for telegram functionality idc about

    return contacts


def load_google_contacts(path: str, encoding: str = "utf-8") -> list[dict[str, str]]:
    with open(path, "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file)
        contacts = list(reader)

    return contacts


def normalise_telegram_contact(contact: dict[str, str]) -> None:
    phone_number = contact.get("phone_number", "")

    contact["phone_number"] = (
        phone_number.replace(" ", "").replace("(", "").replace(")", "")
    )

    if contact["phone_number"].startswith("00"):
        contact["phone_number"] = "+" + contact["phone_number"][2:]

    contact.pop("date", None)
    contact.pop("date_unixtime", None)


def clean_telegram_contacts(contacts: list[dict[str, str]]) -> list[dict[str, str]]:
    cleaned = []

    for contact in contacts:
        if not contact.get("phone_number"):
            continue

        if not (contact.get("first_name") or contact.get("last_name")):
            continue

        normalise_telegram_contact(contact)
        cleaned.append(contact)

    return cleaned


# For Comparison Normalisation only
def normalise(phone_number: str) -> str:
    phone_number = phone_number.replace(" ", "").replace("(", "").replace(")", "")

    if phone_number.startswith("00"):
        phone_number = phone_number[2:]

    if phone_number.startswith("380"):
        phone_number = phone_number[3:]
    elif phone_number.startswith("38"):
        phone_number = phone_number[2:]
    elif phone_number.startswith("440"):
        phone_number = phone_number[3:]
    elif phone_number.startswith("44"):
        phone_number = phone_number[2:]

    return phone_number


def create_duplicates_set(contacts: list[dict[str, str]]) -> set[str]:
    return {normalise(contact["Phone 1 - Value"]) for contact in contacts}


def create_google_payload(
    contacts: list[dict[str, str]], duplicates_set: set[str]
) -> list[dict[str, str]]:
    final_payload = []

    for contact in contacts:
        first_name = contact.get("first_name", "")
        last_name = contact.get("last_name", "")
        phone_number = contact.get("phone_number", "")
        labels = "* Telegram"

        if normalise(phone_number) in duplicates_set:
            continue

        final_payload.append(
            dict(
                zip(GOOGLE_CONTACT_HEADERS, [first_name, last_name, labels, "Mobile", phone_number])
            )
        )

    return final_payload


def write_to_csv(contacts: list[dict[str, str]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=GOOGLE_CONTACT_HEADERS)
        writer.writeheader()
        writer.writerows(contacts)



# CHANGE TEST DIRECTORY TO DIRECTORY WITH YOUR CONTACT FILES
if __name__ == "__main__":
    telegram_contacts = load_telegram_contacts("test_data/telegram-contacts.json")
    google_contacts = load_google_contacts("test_data/google-contacts.csv")

    telegram_contacts = clean_telegram_contacts(telegram_contacts)
    duplicates_set = create_duplicates_set(google_contacts)
    final_payload = create_google_payload(telegram_contacts, duplicates_set)

    write_to_csv(final_payload, "test_data/final-payload.csv")
