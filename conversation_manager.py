class ConversationManager:

    def __init__(self):
        self.turns = []

    def start_turn(self, user_message):
        turn = {
            "user_message": user_message,
            "messages": [],
            "status": "in_progress"
        }

        self.turns.append(turn)

        return turn
    
    def add_message(self, turn, message):
        turn["messages"].append(message)

        print("Message count:", len(turn["messages"]))
        print("Message size:", len(str(message)), "characters")

    def complete_turn(self, turn):
        turn["status"] = "completed"

    def get_completed_turns(self):
        return [
            turn
            for turn in self.turns
            if turn["status"] == "completed"
        ]

    def get_messages(self):
        messages = []

        for turn in self.turns:
            messages.append({
                "role": "user",
                "parts": [
                    {"text": turn["user_message"]}
                ]
            })

            messages.extend(turn["messages"])

        return messages

    def get_latest_turn(self):
        if not self.turns:
            return None

        return self.turns[-1]

    def remove_oldest_completed_turn(self):
        for index, turn in enumerate(self.turns):
            if turn["status"] == "completed":
                self.turns.pop(index)
                return True

        return False

    def remove_turn(self, turn):
        if turn in self.turns:
            self.turns.remove(turn)

    def compact_active_turn(self, turn, keep_last=4):
        messages = turn["messages"]

        start_index = max(0, len(messages) - keep_last)

        def has_function_call(message):
            parts = (
                message.parts
                if hasattr(message, "parts")
                else message.get("parts", [])
            )

            for part in parts:
                if isinstance(part, dict):
                    if part.get("function_call"):
                        return True
                elif getattr(part, "function_call", None):
                    return True

            return False

        if start_index > 0:
            previous_message = messages[start_index - 1]

            if has_function_call(previous_message):
                start_index -= 1

        turn["messages"] = messages[start_index:]