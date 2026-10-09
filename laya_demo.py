#!/usr/bin/env python3
"""
Laya demonstration - showcasing capabilities without model download
Focuses on question presets and utility functions
"""

import os
import laya.presets
from laya import detect_language, detect_script, confidence_from_probs

def demonstrate_presets():
    """Demonstrate laya's question presets for various analysis tasks"""
    print("🔍 LAYA QUESTION PRESETS DEMONSTRATION")
    print("=" * 60)
    
    presets = {
        "🛡️  Guard Questions (AI Safety)": laya.presets.guard_questions(),
        "📊 Moderation Questions (Content Quality)": laya.presets.moderation_questions(),
        "📧 Email Questions (Email Routing)": laya.presets.email_questions(),
        "🔀 Router Questions (Request Classification)": laya.presets.router_questions(),
        "🎯 Triage Questions (Customer Service)": laya.presets.triage_questions()
    }
    
    for preset_name, questions in presets.items():
        print(f"\n{preset_name}")
        print("-" * 50)
        for qid, question in questions.items():
            qtype = question.get('type', 'unknown')
            instructions = question.get('instructions', 'No instructions')
            print(f"  • {qid}")
            print(f"    {instructions}")
            print(f"    Type: {qtype}")
            
            if qtype == 'choice' and 'criteria' in question:
                criteria = question['criteria']
                if isinstance(criteria, dict):
                    print(f"    Options: {', '.join(list(criteria.keys())[:5])}{'...' if len(criteria) > 5 else ''}")
                else:
                    print(f"    Options: {criteria}")
            elif qtype == 'score' and 'criteria' in question:
                criteria = question['criteria']
                print(f"    Scale: {criteria}")
            print()

def demonstrate_utilities():
    """Demonstrate laya's utility functions"""
    print("\n🔧 LAYA UTILITY FUNCTIONS DEMONSTRATION")
    print("=" * 60)
    
    # Test text samples
    test_texts = [
        "Hello, how are you today?",
        "您好，今天天气不错！",
        "SELECT * FROM users WHERE id = 1;",
        "def hello_world():\n    print('Hello, World!')",
        "《三体》是一部伟大的科幻小说。",
        "I need to refund this customer's payment immediately.",
        "This is absolutely terrible service! I'm furious!",
        "Let's schedule a meeting for next Tuesday at 2 PM."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Text {i}: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        try:
            lang = detect_language(text)
            print(f"   🔤 Language: {lang}")
        except Exception as e:
            print(f"   🔤 Language detection error: {e}")
        
        try:
            script = detect_script(text)
            print(f"   📝 Script: {script}")
        except Exception as e:
            print(f"   📝 Script detection error: {e}")
        
        # Show confidence scoring with example probabilities
        if i == 1:  # Just show once for demo
            print(f"\n   📊 Confidence Scoring Example:")
            probs_examples = [
                ([0.9, 0.05, 0.05], "High confidence"),
                ([0.4, 0.35, 0.25], "Low confidence"), 
                ([0.33, 0.33, 0.34], "Uniform distribution")
            ]
            for probs, desc in probs_examples:
                try:
                    conf = confidence_from_probs(probs)
                    print(f"      {desc} {probs} → {conf:.3f}")
                except Exception as e:
                    print(f"      Confidence error: {e}")

def demonstrate_analysis_use_case():
    """Show how these could be used for Obsidian vault analysis"""
    print("\n💡 PRACTICAL USE CASE: Obsidian Vault Analysis")
    print("=" * 60)
    print("Laya can help analyze your knowledge base by:")
    print()
    print("🛡️  Guard Questions:")
    print("   • Detect potential jailbreak attempts in notes")
    print("   • Identify prompt injection risks") 
    print("   • Flag sensitive personal data exposure")
    print("   • Assess harm severity of technical advice")
    print("   • Classify note topics (coding, general_knowledge, etc.)")
    print()
    print("📊 Moderation Questions:")
    print("   • Check for toxic or harassing content")
    print("   • Identify threats or calls for violence")
    print("   • Detect spam or low-quality content")
    print("   • Assess overall severity of rule violations")
    print()
    print("🔀 Router Questions:")
    print("   • Estimate reasoning difficulty of notes")
    print("   • Classify knowledge domains (code, math, writing, etc.)")
    print("   • Determine if external tools are needed for understanding")
    print("   • Flag notes with money/legal/safety implications")
    print()
    print("🤖 Combined with Laya Agent:")
    print("   • Actually answer these questions using AI")
    print("   • Create intelligent knowledge base categorization")
    print("   • Automate content safety reviews")
    print("   • Build smart note routing systems")

def main():
    """Run the demonstration"""
    print("🚀 LAYA CAPABILITIES DEMONSTRATION")
    print("Showing how Laya can be used for knowledge analysis")
    print("=" * 60)
    
    demonstrate_presets()
    demonstrate_utilities() 
    demonstrate_analysis_use_case()
    
    print("\n" + "=" * 60)
    print("✅ Demonstration complete!")
    print("💡 To use Laya's full AI capabilities, initialize:")
    print("   from laya import Agent")
    print("   agent = Agent()  # Downloads model on first use")
    print("   # Then use agent to answer the question presets")
    print("=" * 60)

if __name__ == "__main__":
    main()