# GBrain Phase 2-4 瀹炴柦璁″垝

**寮€濮嬫椂闂?*: 2026-04-11
**鐩爣**: 瀹屾垚 GBrain 鏍稿績鍔熻兘鐨勫畬鏁村疄鐜?
---

## Phase 2: 澧炲己鍔熻兘

### 2.1 Dream Cycle锛堝闂寸淮鎶わ級

**鐩爣**: 瀹炵幇澶滈棿鑷姩缁存姢浠诲姟

**瀹炵幇姝ラ**:
1. 鍒涘缓 `scripts/dream_cycle.py`
2. 瀹炵幇浠ヤ笅鍔熻兘锛?   - 鎵弿浠婂ぉ鐨勬墍鏈夊璇?   - 涓板瘜缂哄け鐨勫疄浣?   - 淇鎹熷潖鐨勫紩鐢?   - 宸╁浐璁板繂
   - 鐢熸垚 DREAMS.md

**浠ｇ爜缁撴瀯**:
```python
class ErbingDreamCycle:
    """姊﹀寰幆 - 澶滈棿鑷姩缁存姢"""

    def run_dream_cycle(self):
        """澶滈棿杩愯"""
        # 1. 鎵弿浠婂ぉ鐨勬墍鏈夊璇?        today_conversations = self.get_today_conversations()

        # 2. 涓板瘜缂哄け鐨勫疄浣?        for conv in today_conversations:
            entities = self.detect_entities(conv)
            for entity in entities:
                if not self.memory.has_rich_page(entity):
                    self.enrich_in_background(entity)

        # 3. 淇鎹熷潖鐨勫紩鐢?        self.fix_broken_citations()

        # 4. 宸╁浐璁板繂
        self.consolidate_memories()

        # 5. 鐢熸垚 DREAMS.md
        self.generate_dream_report()
```

### 2.2 Cross-Reference Back-Links锛堜氦鍙夊紩鐢級

**鐩爣**: 瀹炵幇閾佸緥 - 姣忎釜瀹炰綋椤甸潰蹇呴』閾炬帴鍒版墍鏈夊紩鐢ㄥ畠鐨勫叾浠栭〉闈?
**瀹炵幇姝ラ**:
1. 鍒涘缓 `memory/database/cross_reference.py`
2. 瀹炵幇鍙嶅悜閾炬帴鍔熻兘
3. 鍦ㄦ瘡娆℃洿鏂板疄浣撻〉闈㈡椂鑷姩娣诲姞鍙嶅悜閾炬帴

**浠ｇ爜缁撴瀯**:
```python
def update_entity_page(entity, new_info):
    """鏇存柊瀹炰綋椤甸潰"""

    # 鏇存柊椤甸潰
    page = erbing.get(entity)
    page.timeline.append(new_info)

    # 鎵惧埌鎵€鏈夋彁鍙婃瀹炰綋鐨勫叾浠栭〉闈?    mentions = erbing.find_mentions(entity)

    # 娣诲姞鍙嶅悜閾炬帴
    for mention in mentions:
        mention.add_backlink(
            f"- Referenced in [{mention.title}]({mention.path}) -- {new_info.summary}"
        )
```

### 2.3 Enrichment Tier锛堜赴瀵屽寲鍒嗙骇锛?
**鐩爣**: 瀹炵幇3绾т赴瀵屽寲绯荤粺

**瀹炵幇姝ラ**:
1. 鍒涘缓 `memory/database/enrichment_tier.py`
2. 瀹炵幇Tier鍒嗙骇绯荤粺锛?   - Tier 1: 鍏抽敭浜哄憳鍜屽叕鍙革紙10-15 API璋冪敤锛?   - Tier 2: 鍊煎緱娉ㄦ剰鐨勪汉鍛橈紙3-5 API璋冪敤锛?   - Tier 3: 娆¤鎻愬強锛?-2 API璋冪敤锛?
**浠ｇ爜缁撴瀯**:
```python
class EnrichmentTier:
    """涓板瘜鍖栧垎绾х郴缁?""

    def classify_tier(self, entity):
        """鍒嗙被瀹炰綋灞傜骇"""
        # Tier 1: 鍏抽敭浜哄憳鍜屽叕鍙?        if entity in self.core_circle:
            return 1
        # Tier 2: 鍊煎緱娉ㄦ剰鐨勪汉鍛?        elif entity in self.notable_contacts:
            return 2
        # Tier 3: 娆¤鎻愬強
        else:
            return 3

    def enrich(self, entity, tier):
        """鎸夊眰绾т赴瀵?""
        if tier == 1:
            return self.full_enrichment(entity)
        elif tier == 2:
            return self.standard_enrichment(entity)
        else:
            return self.minimal_enrichment(entity)
```

---

## Phase 3: 鏌ヨ浼樺寲

### 3.1 Brain-First Lookup Protocol锛堝ぇ鑴戜紭鍏堟煡鎵撅級

**鐩爣**: 鍦ㄨ皟鐢ㄤ换浣曞閮ˋPI涔嬪墠锛屽厛妫€鏌ュぇ鑴?
**瀹炵幇姝ラ**:
1. 鍒涘缓 `memory/database/brain_first_lookup.py`
2. 瀹炵幇澶ц剳浼樺厛鏌ユ壘鍗忚

**浠ｇ爜缁撴瀯**:
```python
def research_entity(name):
    """鐮旂┒瀹炰綋 - 澶ц剳浼樺厛"""

    # 1. gbrain search锛堝叧閿瘝鍖归厤锛?    results = erbing.search(name, strategy="keyword")

    # 2. gbrain query锛堟贩鍚堟悳绱級
    results = erbing.search(f"what do we know about {name}", strategy="balanced")

    # 3. gbrain get锛堢洿鎺ヨ鍙栵級
    if results:
        page = erbing.get(slug)

    # 4. 澶栭儴API浠呬綔涓哄悗澶?    if not results or page.is_thin():
        results = external_api_search(name)

    return results
```

### 3.2 娣峰悎鎼滅储浼樺寲

**鐩爣**: 浼樺寲鍥涚瓥鐣ユ绱㈢郴缁?
**瀹炵幇姝ラ**:
1. 浼樺寲 `memory/database/retrieval_strategies.py`
2. 瀹炵幇RRF铻嶅悎
3. 瀹炵幇Cross-Encoder閲嶆帓搴?
### 3.3 鎬ц兘浼樺寲

**鐩爣**: 浼樺寲鏌ヨ鎬ц兘

**瀹炵幇姝ラ**:
1. 娣诲姞缂撳瓨灞?2. 浼樺寲鏁版嵁搴撴煡璇?3. 瀹炵幇鎵归噺鎿嶄綔

---

## Phase 4: 楂樼骇鍔熻兘

### 4.1 瀹屾暣鐨凟nrichment Pipeline锛?姝ュ崗璁級

**鐩爣**: 瀹炵幇瀹屾暣鐨?姝ヤ赴瀵屽寲娴佺▼

**瀹炵幇姝ラ**:
1. 鍒涘缓 `memory/database/enrichment_pipeline.py`
2. 瀹炵幇浠ヤ笅姝ラ锛?   - Step 1: 璇嗗埆瀹炰綋
   - Step 2: 妫€鏌ュぇ鑴戠姸鎬?   - Step 3: 浠庢潵婧愭彁鍙栦俊鍙?   - Step 4: 鏁版嵁婧愭煡璇?   - Step 5: 淇濆瓨鍘熷鏁版嵁
   - Step 6: 鍐欏叆澶ц剳
   - Step 7: 浜ゅ弶寮曠敤

**浠ｇ爜缁撴瀯**:
```python
class EnrichmentPipeline:
    """7姝ヤ赴瀵屽寲娴佺▼"""

    def run(self, entity):
        """杩愯瀹屾暣娴佺▼"""

        # Step 1: 璇嗗埆瀹炰綋
        entity_info = self.identify_entity(entity)

        # Step 2: 妫€鏌ュぇ鑴戠姸鎬?        page = self.check_brain_state(entity)

        # Step 3: 浠庢潵婧愭彁鍙栦俊鍙?        signals = self.extract_signals(entity_info)

        # Step 4: 鏁版嵁婧愭煡璇?        data = self.query_data_sources(entity, signals)

        # Step 5: 淇濆瓨鍘熷鏁版嵁
        self.save_raw_data(entity, data)

        # Step 6: 鍐欏叆澶ц剳
        self.write_to_brain(entity, data, page)

        # Step 7: 浜ゅ弶寮曠敤
        self.cross_reference(entity, data)
```

### 4.2 楂樼骇鍔熻兘

**鐩爣**: 瀹炵幇楂樼骇鍔熻兘

**瀹炵幇姝ラ**:
1. 瀹炰綋鍏崇郴鍥?2. 姒傚康鑱氱被
3. 鍘熷垱鎯虫硶绱㈠紩

### 4.3 鐢熶骇閮ㄧ讲

**鐩爣**: 鐢熶骇鐜閮ㄧ讲

**瀹炵幇姝ラ**:
1. 閰嶇疆绠＄悊
2. 鐩戞帶鍜屾棩蹇?3. 閿欒澶勭悊
4. 鎬ц兘鐩戞帶

---

## 瀹炴柦鏃堕棿琛?
| Phase | 浠诲姟 | 棰勮鏃堕棿 | 鐘舵€?|
|-------|------|---------|------|
| Phase 1 | 鏍稿績妯″紡 | 宸插畬鎴?| 鉁?|
| Phase 2 | 澧炲己鍔熻兘 | 宸插畬鎴?| 鉁?|
| Phase 3 | 鏌ヨ浼樺寲 | 2-3澶?| 馃搵 |
| Phase 4 | 楂樼骇鍔熻兘 | 3-5澶?| 馃搵 |

---

## 涓嬩竴姝ヨ鍔?
1. 鉁?鍒涘缓 Phase 2-4 瀹炴柦璁″垝鏂囨。
2. 馃毀 寮€濮嬪疄鏂?Phase 2.1 Dream Cycle
3. 馃搵 瀹炴柦 Phase 2.2 Cross-Reference
4. 馃搵 瀹炴柦 Phase 2.3 Enrichment Tier

---

*鍒涘缓鏃堕棿: 2026-04-11*
*鐗堟湰: v1.0*

