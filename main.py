from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return False


class TerminationState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return True


class AsciiState(State):
    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.symb = symbol

    def check_self(self, char: str) -> bool:
        return char == self.symb


class StarState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char: str) -> bool:
        for state in self.next_states:
            if state.check_self(char):
                return True
        return False


class PlusState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()

        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            new_state = self.__init_next_state(char, tmp_next_state)

            if char not in ["*", "+"] and tmp_next_state != self.curr_state:
                    prev_state = tmp_next_state

            prev_state.next_states = [new_state]
            tmp_next_state = new_state

        tmp_next_state.next_states = [TerminationState()]

    def __init_next_state(self, next_token: str, tmp_next_state: State) -> State:
        if next_token == ".":
            return DotState()

        if next_token == "*":
            return StarState(tmp_next_state)

        if next_token == "+":
            return PlusState(tmp_next_state)

        if next_token.isascii():
            return AsciiState(next_token)

        raise AttributeError("Character is not supported")

    def check_string(self, string: str) -> bool:

        def match(state: State, idx: int) -> bool:
            if isinstance(state, TerminationState):
                return idx == len(string)

            if idx == len(string):
                if isinstance(state, StarState) or isinstance(state, StartState):
                    return any(match(nxt, idx) for nxt in state.next_states)
                return False

            char = string[idx]

            if isinstance(state, StartState):
                return any(match(nxt, idx) for nxt in state.next_states)

            if isinstance(state, StarState):
                if state.checking_state.check_self(char):
                    if match(state, idx + 1):
                        return True
                return any(match(nxt, idx) for nxt in state.next_states)

            if isinstance(state, PlusState):
                if state.checking_state.check_self(char):
                    if match(state, idx + 1):
                        return True
                    return any(match(nxt, idx + 1) for nxt in state.next_states)
                return False

            if state.check_self(char):
                return any(match(nxt, idx + 1) for nxt in state.next_states)

            return False

        return match(self.curr_state, 0)

def run_cli_interface():
    print("=" * 40)
    print(" Regex FSM Тестер")
    print("=" * 40)
    print("Команди: 'exit' - вийти, 'back' - змінити регулярний вираз\n")

    while True:
        pattern = input("Введіть регулярний вираз (або 'exit'): ").strip()
        if pattern.lower() == 'exit':
            print("Роботу завершено.")
            break

        if not pattern:
            print("Вираз не може бути порожнім.")
            continue

        try:
            regex_compiled = RegexFSM(pattern)
            print(f" Шаблон '{pattern}' успішно скомпільовано!")
        except Exception as e:
            print(f" Помилка компіляції шаблону: {e}")
            continue

        print("-" * 20)
        while True:
            test_string = input(f"[{pattern}] Введіть рядок для перевірки: ").strip()

            if test_string.lower() == 'back':
                print("\nПовернення до вводу нового шаблону...")
                break
            if test_string.lower() == 'exit':
                print("Роботу завершено.")
                return

            try:
                result = regex_compiled.check_string(test_string)
                if result:
                    print("   🟢 Рядок ВІДПОВІДАЄ шаблону")
                else:
                    print("   🔴 Рядок НЕ відповідає шаблону")
            except Exception as e:
                print(f"   Помилка під час перевірки: {e}")


if __name__ == "__main__":
    run_cli_interface()

# if __name__ == "__main__":
#     regex_pattern = "a*4.+hi"
#     regex_compiled = RegexFSM(regex_pattern)

#     print(regex_compiled.check_string("aaaaaa4uhi"))
#     print(regex_compiled.check_string("4uhi"))
#     print(regex_compiled.check_string("meow"))
