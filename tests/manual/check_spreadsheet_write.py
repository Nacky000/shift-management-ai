from Spreadsheet import spreadsheet

if __name__ == "__main__":
    user_id = "U27270693436a29fa7e5a884e4663dd99"

    task = {
        "date": "2026-10-25",
        "start_time": "18:00",
        "end_time": "21:00"
    }

    result = spreadsheet.write_schedule(user_id, task)
    print(result)

# spreadsheet.setup_user_status_dropdown()