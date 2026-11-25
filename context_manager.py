class ContextManager:

    def __init__(self):
        self.original_task = None
        self.task_status = "not_started"
        self.conversation_summary = ""
        self.task_summary = ""

        self.task_state = {
            "repository": None,
            "inspected_files": [],
            "findings": [],
            "pending": []
        }

    def start_task(self, user_message):
        self.original_task = user_message
        self.task_status = "active"
        self.task_summary = ""

        self.task_state = {
            "repository": None,
            "inspected_files": [],
            "findings": [],
            "pending": []
        }

    def complete_task(self):
        self.task_status = "completed"

    def set_repository(self, owner, repo):
        self.task_state["repository"] = f"{owner}/{repo}"

    def add_inspected_file(self, file_path):
        if file_path not in self.task_state["inspected_files"]:
            self.task_state["inspected_files"].append(file_path)

    def add_finding(self, finding):
        self.task_state["findings"].append(finding)

    def add_pending_task(self, task):
        if task not in self.task_state["pending"]:
            self.task_state["pending"].append(task)

    def update_summary(self, new_summary):
        self.conversation_summary = new_summary

    def get_task_context(self):
        return {
            "original_task": self.original_task,
            "conversation_summary": self.conversation_summary,
            "task_summary": self.task_summary,
            "task_state": self.task_state,
            "task_status": self.task_status
        }

    def update_task_summary(self, new_summary):
        self.task_summary = new_summary