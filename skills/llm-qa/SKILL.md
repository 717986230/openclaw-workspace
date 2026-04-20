---
name: llm-qa
description: LLM intelligent Q&A system with dialogue, knowledge graph Q&A, and multi-turn conversation support.
triggers:
  - "qa"
  - "question answering"
  - "dialogue"
  - "knowledge graph qa"
  - "multi-turn"
dependencies:
  - tool: read
  - tool: write
  - tool: exec
  - library: sqlite3
  - library: json
  - library: typing
  - library: dataclasses
  - library: enum
  - library: re
capabilities:
  - question_answering
  - dialogue
  - knowledge_graph_qa
  - multi_turn_conversation
  - context_building
  - relevance_scoring
---

# LLM QA Skill

This skill provides an LLM intelligent Q&A system with dialogue, knowledge graph Q&A, and multi-turn conversation support.

## How It Works

1.  **Question Answering:** Answers questions based on relevant memories.
2.  **Dialogue:** Maintains dialogue history for conversational interactions.
3.  **Knowledge Graph Q&A:** Answers questions using knowledge graph information.
4.  **Multi-Turn Conversation:** Maintains context across multiple turns.
5.  **Relevance Scoring:** Scores memories based on relevance to the query.

## Usage

### Basic Operations

**Answer Question:**
```python
qa = LLMIntelligentQA(db_path)
qa.load_memories(limit=1000)
result = qa.answer_question("What is Python?", max_results=5)
```

**Dialogue:**
```python
result = qa.dialogue("user1", "Tell me about Python")
```

**Knowledge Graph Q&A:**
```python
result = qa.knowledge_graph_qa("What is Python?", max_results=5)
```

### Advanced Operations

**Multi-Turn Q&A:**
```python
result = qa.multi_turn_qa("user1", "What about machine learning?", max_results=5)
```

**Clear Dialogue History:**
```python
qa.clear_dialogue_history("user1")
```

## Examples

### Example 1: Answering Questions
**User:** "What is Python?"
**Agent:** [Finds relevant memories and generates an answer]

### Example 2: Dialogue
**User:** "Tell me about Python."
**Agent:** [Maintains dialogue history and responds conversationally]

### Example 3: Multi-Turn Conversation
**User:** "What about machine learning?"
**Agent:** [Builds context from previous turns and answers]

## Key Features

- **Multiple Q&A Modes:** Supports simple Q&A, dialogue, knowledge graph Q&A, and multi-turn conversation.
- **Context Awareness:** Maintains context across multiple turns.
- **Relevance Scoring:** Scores memories based on relevance to the query.
- **Dialogue History:** Maintains dialogue history for each user.
- **Flexible Retrieval:** Supports flexible memory retrieval with relevance scoring.

## Dependencies

- **Python Libraries:** `sqlite3`, `json`, `typing`, `dataclasses`, `enum`, `re`

## Best Practices

- **Load Memories:** Always load memories before answering questions.
- **Context Management:** Manage dialogue history to maintain context.
- **Relevance Tuning:** Adjust relevance scoring based on your data.
- **Multi-Turn Strategy:** Use multi-turn Q&A for complex conversations.
- **Clear History:** Clear dialogue history when starting new conversations.

## Contributing

To extend this skill:
1.  Add new Q&A methods to the `LLMIntelligentQA` class.
2.  Update the `SKILL.md` with new capabilities.
3.  Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
