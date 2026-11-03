import asyncio
from app.eval.evaluator import Evaluator

if __name__ == "__main__":
    print(asyncio.run(Evaluator().run()).model_dump_json(indent=2))
