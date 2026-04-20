#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from high_concurrency_ultimate import UltimateDistributedSystem, Node

async def main():
    config_path = Path(r'C:\Users\Administrator\.openclaw\workspace\memory\database\config_ultimate.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print('=' * 60)
    print(f'Starting {config["system"]["name"]} v{config["system"]["version"]}')
    print(f'Environment: {config["system"]["environment"]}')
    print('=' * 60)
    
    system = UltimateDistributedSystem(config)
    
    print('\nInitializing system...')
    await system.initialize()
    print('System initialized successfully')
    
    print('\nRegistering nodes...')
    for node_config in config['nodes']:
        node = Node(
            node_id=node_config['node_id'],
            host=node_config['host'],
            port=node_config['port'],
            weight=node_config.get('weight', 1)
        )
        system.service_discovery.register('main_service', node)
        print(f'  Node {node.node_id} registered')
    
    print('\nSystem status:')
    stats = system.get_stats()
    print(json.dumps(stats, indent=2, default=str))
    
    print('\nRunning performance test...')
    await system.run_performance_test()
    
    print('\nSystem running... (Press Ctrl+C to stop)')
    try:
        while True:
            await asyncio.sleep(10)
            current_stats = system.get_stats()
            print(f'\nLive stats: {current_stats["total_tasks_processed"]} tasks processed')
    except KeyboardInterrupt:
        print('\nShutting down system...')
        await system.shutdown()
        print('System shutdown complete')

if __name__ == "__main__":
    asyncio.run(main())
