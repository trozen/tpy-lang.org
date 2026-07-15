# expect: ok
class AppError(Exception):
    pass

class ParseError(AppError):
    pass

def main():
    try:
        raise ParseError("bad")
    except AppError as e:
        print("caught as base:", str(e))
    try:
        try:
            raise ParseError("inner")
        except ParseError:
            print("re-raising")
            raise
    except AppError:
        print("re-raise caught")

main()
