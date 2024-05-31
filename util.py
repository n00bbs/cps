import asyncio

def callback_helper(func: function | None, *args, **kwargs):
  if func is not None:
    return func(*args, **kwargs) # type: ignore
  return None

def run_task_factory(func: function):
  last_task: list[asyncio.Task | None] = [None]
  def run_task(*args, **kwargs):
    if last_task[0] is not None:
      last_task[0].cancel()
    last_task[0] = asyncio.create_task(func(*args, **kwargs))
  return run_task