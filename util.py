import asyncio

def callback_helper(func: function | None, *args, **kwargs):
  print("callback_helper", func, args, kwargs)
  if func is not None:
    print("callback_helper", "calling")
    return callable(*args, **kwargs)
  return None

def run_task_factory(func: function, *args, **kwargs):
  last_task = [None]
  def run_task():
    if last_task[0] is not None:
      last_task[0].cancel()
    last_task[0] = asyncio.create_task(func(*args, **kwargs))
  return run_task