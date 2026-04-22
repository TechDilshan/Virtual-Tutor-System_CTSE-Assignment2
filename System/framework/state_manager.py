class StateManager:
    def __init__(self):
        self.global_state = {}

    def update_state(self, key, value):
        """
        Update the global state for the system.
        """
        self.global_state[key] = value

    def get_state(self, key):
        """
        Retrieve the current state of a specific key.
        """
        return self.global_state.get(key, None)

    def clear_state(self):
        """
        Clear all global state data.
        """
        self.global_state = {}