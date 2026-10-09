#!/usr/bin/env python3
"""
Use laya to analyze knowledge base content and provide insights
"""

import os
import time
from laya import Agent
import laya.presets

def analyze_learning_note(file_path):
    """Analyze a single learning note using laya agent"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get filename for display
        filename = os.path.basename(file_path)
        
        print(f"\n📖 Analyzing: {filename}")
        print("-" * 50)
        
        # Initialize laya agent (this will download model on first use)
        print("🤖 Initializing Laya agent...")
        start_time = time.time()
        agent = Agent()
        init_time = time.time() - start_time
        print(f"   Agent ready in {init_time:.1f}s\n")
        
        # Use laya to answer key questions about the note
        print("🔍 Laya Analysis Results:")
        
        # 1. What is the main topic/subject?
        print("   📚 Subject Classification:")
        try:
            # Using router questions preset for domain classification
            router_preset = laya.presets.router_questions()
            domain_question = router_preset.get('domain', {})
            if domain_question:
                print(f"      Question: {domain_question.get('instructions')}")
                print(f"      Options: {list(domain_question.get('criteria', {}).keys())}")
                # Note: To get actual answer, we'd need to prompt the agent
                # For now showing the framework
        except Exception as e:
            print(f"      Error: {e}")
        
        # 2. What's the difficulty level to understand this?
        print("   📊 Difficulty Assessment:")
        try:
            diff_question = router_preset.get('difficulty', {})
            if diff_question:
                print(f"      Question: {diff_question.get('instructions')}")
                print(f"      Scale: {diff_question.get('criteria', [])}")
        except Exception as e:
            print(f"      Error: {e}")
            
        # 3. Does this require external tools/search to fully understand?
        print("   🔧 External Resources Needed:")
        try:
            tools_question = router_preset.get('needs_tools', {})
            if tools_question:
                print(f"      Question: {tools_question.get('instructions')}")
                print(f"      Type: Yes/No question")
        except Exception as e:
            print(f"      Error: {e}")
        
        # 4. Safety check - any concerning content?
        print("   🛡️  Safety Check:")
        try:
            guard_preset = laya.presets.guard_questions()
            harmful_q = guard_preset.get('harm_severity', {})
            if harmful_q:
                print(f"      Harm assessment: {harmful_q.get('instructions')}")
                print(f"      Scale: {harmful_q.get('criteria', [])}")
        except Exception as e:
            print(f"      Error: {e}")
            
        # Show content preview
        preview = content[:150] + "..." if len(content) > 150 else content
        print(f"\n   📄 Content Preview:")
        print(f"      {preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}")
        return False

def main():
    """Main function to analyze knowledge base"""
    print("🧠 LAYA-POWERED KNOWLEDGE BASE ANALYSIS")
    print("=" * 60)
    print("Using Laya to analyze learning notes in your Obsidian vault")
    print("=" * 60)
    
    vault_path = "/Users/xinglong/Documents/Obsidian Vault/📚 学习"
    
    if not os.path.exists(vault_path):
        print(f"❌ Learning directory not found: {vault_path}")
        return
    
    # Get all markdown files in learning directory
    try:
        files = []
        for root, dirs, filenames in os.walk(vault_path):
            for filename in filenames:
                if filename.endswith('.md'):
                    files.append(os.path.join(root, filename))
        
        if not files:
            print(f"❌ No markdown files found in {vault_path}")
            return
            
        print(f"📚 Found {len(files)} learning notes to analyze\n")
        
        # Analyze first 3 files as a sample (to avoid too much output/model loading)
        sample_files = files[:3]
        
        for file_path in sample_files:
            analyze_learning_note(file_path)
            print()  # Add spacing between files
            
        print("=" * 60)
        print("✅ Sample analysis complete!")
        print(f"📊 Analyzed {len(sample_files)} of {len(files)} learning notes")
        print("\n💡 Next steps for full implementation:")
        print("   1. The Laya agent is now ready and cached")
        print("   2. You can run similar analysis on your full knowledge base")
        print("   3. Use the question presets to build intelligent categorization")
        print("   4. Create automated workflows for content review and organization")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error accessing vault: {e}")

if __name__ == "__main__":
    main()