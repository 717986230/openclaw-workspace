#!/usr/bin/env python3
"""
nn_bridge.py - Pure NumPy Neural Network for Erbing Memory System
No external ML deps: only numpy. Drop-in for synaptic/MLP.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

DB_PATH = Path(__file__).parent / "xiaozhi_memory.db"

# ── Activation helpers ────────────────────────────────────────────────────────

def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_d(x: np.ndarray) -> np.ndarray:
    s = sigmoid(x)
    return s * (1 - s)

def tanh(x: np.ndarray) -> np.ndarray:
    return np.tanh(x)

def tanh_d(x: np.ndarray) -> np.ndarray:
    return 1.0 - np.tanh(x) ** 2

def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)

def relu_d(x: np.ndarray) -> np.ndarray:
    return (x > 0).astype(float)


# ── Text Encoding ─────────────────────────────────────────────────────────────

CATEGORIES = [
    "identity", "relationship", "principle", "skill", "learning",
    "event", "reminder", "knowledge", "project", "error"
]

TAG_POOL = [
    "brain.js", "neural-network", "memory", "skill", "learning",
    "identity", "project", "code", "api", "database", "bug",
    "feature", "improvement", "config", "channel", "feishu", "discord",
    "github", "evolution", "erbing"
]

CHAR_DIM = 128   # character embedding dimension


def char_encode(text: str, dim: int = CHAR_DIM) -> np.ndarray:
    """Character-trigram bag vector."""
    vec = np.zeros(dim)
    text = text.lower()
    for i, ch in enumerate(text):
        vec[ord(ch) % dim] += 1.0
    # Trigrams
    for i in range(len(text) - 2):
        tri = (ord(text[i]) * 91 + ord(text[i+1]) * 91 + ord(text[i+2])) % dim
        vec[tri] += 0.5
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def encode_combined(text: str, category: str, tags: List[str]) -> np.ndarray:
    """Full feature vector: text(128) + category(10) + tags(19) = 157-dim"""
    text_vec = char_encode(text, CHAR_DIM)
    cat_vec = np.zeros(len(CATEGORIES))
    if category in CATEGORIES:
        cat_vec[CATEGORIES.index(category)] = 1.0
    tag_vec = np.zeros(len(TAG_POOL))
    for tag in tags:
        if tag in TAG_POOL:
            tag_vec[TAG_POOL.index(tag)] = 1.0
    return np.concatenate([text_vec, cat_vec, tag_vec])


# ── NumPy Neural Network ──────────────────────────────────────────────────────

class NeuralNet:
    """Simple multi-layer perceptron in pure numpy."""

    def __init__(self, layers: List[int], activation: str = "sigmoid"):
        self.activation = activation
        act_fn = {"sigmoid": sigmoid, "tanh": tanh, "relu": relu}[activation]
        act_d = {"sigmoid": sigmoid_d, "tanh": tanh_d, "relu": relu_d}[activation]
        self.W = []  # weights
        self.b = []  # biases
        self.act_fn = act_fn
        self.act_d = act_d
        self.activations = []  # store activations for backprop

        for i in range(len(layers) - 1):
            w = np.random.randn(layers[i], layers[i+1]) * np.sqrt(2.0 / (layers[i] + layers[i+1]))
            b = np.zeros(layers[i+1])
            self.W.append(w)
            self.b.append(b)

    def forward(self, x: np.ndarray) -> np.ndarray:
        self.activations = [x]
        a = x
        for i in range(len(self.W)):
            z = a @ self.W[i] + self.b[i]
            a = self.act_fn(z) if i < len(self.W) - 1 else z  # last layer: linear
            self.activations.append(a)
        return a

    def backward(self, y: np.ndarray, lr: float = 0.01):
        m = y.shape[0] if y.ndim > 1 else 1
        # Output layer delta
        delta = self.activations[-1] - y
        grads_w = []
        grads_b = []

        for i in reversed(range(len(self.W))):
            dw = (self.activations[i].T @ delta) / max(m, 1)
            db = np.mean(delta, axis=0)
            grads_w.insert(0, dw)
            grads_b.insert(0, db)
            if i > 0:
                delta = (delta @ self.W[i].T) * self.act_d(self.activations[i])

        for i in range(len(self.W)):
            self.W[i] -= lr * grads_w[i]
            self.b[i] -= lr * grads_b[i]

    def fit(self, X: np.ndarray, Y: np.ndarray, epochs: int = 500,
            lr: float = 0.1, batch_size: int = 32, verbose: bool = False):
        """Train on numpy arrays."""
        m = X.shape[0]
        for ep in range(epochs):
            # Shuffle
            idx = np.random.permutation(m)
            Xs, Ys = X[idx], Y[idx]

            total_loss = 0.0
            for start in range(0, m, batch_size):
                end = min(start + batch_size, m)
                Xb, Yb = Xs[start:end], Ys[start:end]
                out = self.forward(Xb)
                self.backward(Yb, lr)
                total_loss += np.mean((out - Yb) ** 2)

            if verbose and (ep + 1) % 100 == 0:
                print(f"  epoch {ep+1}/{epochs}, loss={total_loss:.4f}")

        final_out = self.forward(X)
        return {"error": float(np.mean((final_out - Y) ** 2))}

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.forward(X)

    def to_json(self) -> Dict:
        return {
            "layers": [w.tolist() for w in self.W],
            "biases": [b.tolist() for b in self.b],
            "activation": self.activation,
        }

    @classmethod
    def from_json(cls, data: Dict) -> 'NeuralNet':
        layers = [len(w) for w in data["layers"]]
        layers.insert(0, len(data["layers"][0][0]))
        net = cls(layers, data.get("activation", "sigmoid"))
        net.W = [np.array(w) for w in data["layers"]]
        net.b = [np.array(b) for b in data["biases"]]
        return net


# ── Model Wrappers ────────────────────────────────────────────────────────────

MODEL_DIR = Path(__file__).parent / "models"

class ImportancePredictor:
    """Predict memory importance (1-10) from content."""

    def __init__(self):
        self.net: Optional[NeuralNet] = None
        self._input_dim = CHAR_DIM + len(CATEGORIES) + len(TAG_POOL)  # 157

    def build(self, hidden: List[int] = [32, 16]):
        layers = [self._input_dim] + hidden + [1]
        self.net = NeuralNet(layers, activation="tanh")
        return self

    def train(self, data: List[Dict], epochs: int = 500, lr: float = 0.1) -> Dict:
        if not self.net:
            self.build()

        X = np.array([encode_combined(d["text"], d["category"], d.get("tags", [])) for d in data])
        Y = np.array([[d["importance"] / 10.0] for d in data])  # normalize 0-1

        result = self.net.fit(X, Y, epochs=epochs, lr=lr, verbose=True)
        return result

    def predict(self, text: str, category: str, tags: List[str]) -> float:
        if not self.net:
            if not self.load():
                return 5.0  # default mid-value
        x = encode_combined(text, category, tags).reshape(1, -1)
        out = self.net.predict(x)[0, 0]
        return min(10.0, max(1.0, round(out * 10)))

    def save(self, path: Optional[Path] = None) -> bool:
        if not self.net:
            return False
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        p = path or (MODEL_DIR / "importance_predictor.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.net.to_json(), f)
        return True

    def load(self, path: Optional[Path] = None) -> bool:
        p = path or (MODEL_DIR / "importance_predictor.json")
        if not p.exists():
            return False
        try:
            with open(p, encoding="utf-8") as f:
                self.net = NeuralNet.from_json(json.load(f))
            return True
        except Exception as e:
            print(f"[NN] Load failed: {e}")
            return False


class MemoryTagger:
    """Multi-label tag prediction for memories."""

    def __init__(self):
        self.net: Optional[NeuralNet] = None
        self._input_dim = CHAR_DIM  # 128
        self._output_dim = len(TAG_POOL)  # 19

    def build(self, hidden: List[int] = [64, 32]):
        layers = [self._input_dim] + hidden + [self._output_dim]
        self.net = NeuralNet(layers, activation="sigmoid")  # sigmoid for multi-label
        return self

    def train(self, data: List[Dict], epochs: int = 300, lr: float = 0.1) -> Dict:
        if not self.net:
            self.build()

        X = np.array([char_encode(d["text"], CHAR_DIM) for d in data])
        Y = np.array([self._tags_to_vec(d.get("tags", [])) for d in data])

        result = self.net.fit(X, Y, epochs=epochs, lr=lr, verbose=True)
        return result

    def _tags_to_vec(self, tags: List[str]) -> np.ndarray:
        vec = np.zeros(self._output_dim)
        for t in tags:
            if t in TAG_POOL:
                vec[TAG_POOL.index(t)] = 1.0
        return vec

    def predict_tags(self, text: str, threshold: float = 0.35) -> List[str]:
        if not self.net:
            if not self.load():
                return []
        x = char_encode(text, CHAR_DIM).reshape(1, -1)
        out = self.net.predict(x)[0]
        return [TAG_POOL[i] for i, v in enumerate(out) if v > threshold]

    def save(self, path: Optional[Path] = None) -> bool:
        if not self.net:
            return False
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        p = path or (MODEL_DIR / "memory_tagger.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.net.to_json(), f)
        return True

    def load(self, path: Optional[Path] = None) -> bool:
        p = path or (MODEL_DIR / "memory_tagger.json")
        if not p.exists():
            return False
        try:
            with open(p, encoding="utf-8") as f:
                self.net = NeuralNet.from_json(json.load(f))
            return True
        except Exception:
            return False


# ── DB Integration ────────────────────────────────────────────────────────────

def tag_new_memories():
    """Re-tag memories that have no tags set."""
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, category FROM memories WHERE tags IS NULL OR tags = ''")
    rows = cursor.fetchall()
    print(f"[TAG] Found {len(rows)} untagged memories")

    tagger = MemoryTagger()
    if not tagger.load():
        print("[TAG] No trained model, skipping")
        conn.close()
        return

    for row in rows:
        mem_id, title, content, category = row
        text = f"{title} {content or ''}"[:200]
        tags = tagger.predict_tags(text)
        if tags:
            cursor.execute("UPDATE memories SET tags = ? WHERE id = ?", (json.dumps(tags), mem_id))
            print(f"  [TAGGED:{mem_id}] {tags} <- {title[:40]}")

    conn.commit()
    conn.close()
    print(f"[TAG] Done. {len(rows)} processed")


def backfill_importance():
    """Use predictor to fill missing importance values."""
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, category, tags FROM memories WHERE importance < 5 OR importance IS NULL")
    rows = cursor.fetchall()
    print(f"[IMPORTANCE] Found {len(rows)} low/empty importance")

    predictor = ImportancePredictor()
    if not predictor.load():
        print("[IMPORTANCE] No trained model, skipping")
        conn.close()
        return

    for row in rows:
        mem_id, title, content, category, tags = row
        text = f"{title} {content or ''}"[:200]
        tags_list = json.loads(tags) if tags else []
        score = predictor.predict(text, category or "knowledge", tags_list)
        cursor.execute("UPDATE memories SET importance = ? WHERE id = ?", (score, mem_id))
        print(f"  [{score}] {title[:40]}")

    conn.commit()
    conn.close()
    print("[IMPORTANCE] Done")


# ── CLI Demo ──────────────────────────────────────────────────────────────────

def demo():
    print("=== Importance Predictor Demo ===")
    predictor = ImportancePredictor()
    predictor.build([32, 16])

    seed_data = [
        {"text": "I am Erbing, evolving AI partner", "category": "identity", "tags": ["identity"], "importance": 9},
        {"text": "大饼 gave me permission to learn skills", "category": "relationship", "tags": ["identity"], "importance": 9},
        {"text": "brain.js integration complete in workspace", "category": "learning", "tags": ["brain.js", "neural-network"], "importance": 8},
        {"text": "Self-improving is my core principle", "category": "principle", "tags": ["skill"], "importance": 9},
        {"text": "Must use SQLite for all memory storage", "category": "reminder", "tags": ["database"], "importance": 10},
        {"text": "Daily status check for gateway", "category": "principle", "tags": ["config"], "importance": 7},
        {"text": "Minor logging note", "category": "knowledge", "tags": ["code"], "importance": 4},
        {"text": "Bug fix in feishu channel handler", "category": "error", "tags": ["bug", "channel"], "importance": 6},
        {"text": "GitHub trending auto PR system", "category": "project", "tags": ["github", "code"], "importance": 7},
        {"text": "Memory database health check script", "category": "skill", "tags": ["database", "code"], "importance": 8},
        {"text": "Evolution cycle monitoring", "category": "skill", "tags": ["evolution"], "importance": 8},
    ]

    print("Training...")
    result = predictor.train(seed_data, epochs=500, lr=0.1)
    print(f"Final MSE: {result['error']:.4f}")

    print("\nPredictions:")
    tests = [
        ("brain.js installed, neural network ready", "learning", ["skill"]),
        ("Must use SQLite for all memory forever", "reminder", ["database"]),
        ("Minor debug log note", "principle", ["config"]),
        ("Evolution cycle checkpoint saved", "learning", ["evolution"]),
    ]
    for text, cat, tags in tests:
        score = predictor.predict(text, cat, tags)
        print(f"  [{int(round(score))}] {text[:50]}")

    predictor.save()
    print("\n=== Memory Tagger Demo ===")
    tagger = MemoryTagger()
    tagger.build([64, 32])

    tag_seed = [
        {"text": "brain.js neural network integration", "tags": ["brain.js", "neural-network"]},
        {"text": "gateway feishu channel debug", "tags": ["channel", "feishu", "bug"]},
        {"text": "memory database schema update", "tags": ["database", "memory"]},
        {"text": "self-improving skill evolution", "tags": ["skill", "learning", "evolution"]},
        {"text": "github trending project analysis", "tags": ["github", "project", "code"]},
        {"text": "erbing identity and persona", "tags": ["identity", "erbing"]},
        {"text": "discord video upload automation", "tags": ["discord", "project", "code"]},
        {"text": "neural network training demo", "tags": ["neural-network", "learning"]},
    ]

    print("Training...")
    result = tagger.train(tag_seed, epochs=300, lr=0.1)
    print(f"Final MSE: {result['error']:.4f}")

    print("\nTag Predictions:")
    for text in [
        "brain.js workspace integration complete",
        "feishu channel configuration",
        "learning self-improving reasoning",
        "github auto PR for trending",
    ]:
        tags = tagger.predict_tags(text)
        print(f"  [{', '.join(tags) or 'none'}] {text}")

    tagger.save()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            demo()
        elif sys.argv[1] == "--tag":
            tag_new_memories()
        elif sys.argv[1] == "--backfill":
            backfill_importance()
        else:
            print("Usage: python nn_bridge.py [--demo|--tag|--backfill]")
    else:
        demo()