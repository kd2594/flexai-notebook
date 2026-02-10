#!/usr/bin/env python3
"""
FlexAI GPU Selector - Standalone Script
Run this to select your GPU from the command line
"""

import httpx
import asyncio
from typing import List, Dict


async def fetch_gpu_types(backend_url: str = "http://backend:8000") -> List[Dict]:
    """Fetch available GPU types"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{backend_url}/api/compute/gpu-types", timeout=5.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"❌ Error fetching GPU types: {e}")
        return []


async def select_gpu(gpu_type: str, backend_url: str = "http://backend:8000") -> Dict:
    """Select and provision a GPU"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/api/compute/instances",
                json={"gpu_type": gpu_type, "gpu_count": 1},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"❌ Error selecting GPU: {e}")
        return {"error": str(e)}


async def check_current_gpu(backend_url: str = "http://backend:8000"):
    """Check currently provisioned GPU"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{backend_url}/api/compute/instances", timeout=5.0)
            response.raise_for_status()
            instances = response.json()
            
            if instances:
                for inst in instances:
                    print(f"\n✅ Currently provisioned: {inst.get('gpu_type', 'Unknown')}")
                    print(f"   Instance ID: {inst.get('id')}")
                    print(f"   Status: {inst.get('status')}")
            else:
                print("\n💻 No GPU currently provisioned - using CPU")
    except Exception as e:
        print(f"❌ Error checking status: {e}")


async def main():
    """Main function"""
    print("=" * 60)
    print("🚀 FlexAI GPU Selector")
    print("=" * 60)
    
    # Check current status
    print("\n📊 Current Status:")
    await check_current_gpu()
    
    # Fetch available GPUs
    print("\n📋 Available GPU Types:")
    gpu_types = await fetch_gpu_types()
    
    if not gpu_types:
        print("No GPU types available")
        return
    
    # Display options
    print("\n0. CPU Only (Free)")
    for i, gpu in enumerate(gpu_types, 1):
        name = gpu.get('name', gpu.get('type', 'Unknown'))
        memory = gpu.get('memory', 'N/A')
        price = gpu.get('price_per_hour', 0)
        print(f"{i}. {name} - {memory} (${price}/hr)")
    
    # Get user input
    print(f"\n{len(gpu_types) + 1}. Check status")
    print(f"{len(gpu_types) + 2}. Exit")
    
    try:
        choice = input("\nEnter your choice: ").strip()
        
        if choice == str(len(gpu_types) + 2) or choice.lower() == 'exit':
            print("👋 Goodbye!")
            return
        
        if choice == str(len(gpu_types) + 1):
            await check_current_gpu()
            return
        
        choice_num = int(choice)
        
        if choice_num == 0:
            gpu_type = "CPU"
        elif 1 <= choice_num <= len(gpu_types):
            gpu_type = gpu_types[choice_num - 1].get('type', gpu_types[choice_num - 1].get('name'))
        else:
            print("❌ Invalid choice")
            return
        
        # Select GPU
        print(f"\n⏳ Provisioning {gpu_type}...")
        result = await select_gpu(gpu_type)
        
        if 'error' not in result:
            print(f"\n✅ Successfully provisioned {gpu_type}!")
            print(f"   Your notebook is now using this compute resource.")
            
            # Show updated status
            await check_current_gpu()
        else:
            print(f"\n❌ Failed to provision: {result.get('message', result.get('error'))}")
    
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
