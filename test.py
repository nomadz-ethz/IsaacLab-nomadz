from isaacgymenvs.tasks import task_registry

task_name = "Isaac-Velocity-Rough-K1-v0"  # replace with your task's registered name
env = task_registry[task_name]()
print("Task initialized successfully!")
env.close()
