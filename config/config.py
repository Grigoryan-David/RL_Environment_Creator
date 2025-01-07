DEFAULT_CONFIG = {
    'board_size': (4, 4),
    'obstacle_count': 4,
    'start': (0, 0),
    'end': (3, 3),
    'rewards': {
        'goal': 1,
        'obstacle': -1,
        'step': 0
    },
    'action_space': ['up', 'down', 'left', 'right'],
    'max_steps': 1000
}

