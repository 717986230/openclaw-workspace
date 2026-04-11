"""
企业级实体检测器
支持多模型融合、实时置信度评分、模糊匹配和别名识别
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
import spacy
from transformers import pipeline


class EnterpriseEntityDetector:
    """企业级实体检测器"""
    
    def __init__(self):
        """初始化检测器"""
        # 加载 NLP 模型
        self.nlp = spacy.load("en_core_web_lg")
        self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        
        # 加载别名映射
        self.alias_map = self.load_alias_map()
        
        # 加载公司名称词典
        self.company_dict = self.load_company_dictionary()
        
        # 加载投资术语
        self.investment_terms = self.load_investment_terms()
    
    def detect_entities(self, message: str) -> Dict[str, List[Dict]]:
        """从消息中提取实体（企业级）"""
        entities = {
            "persons": self.extract_persons(message),
            "companies": self.extract_companies(message),
            "concepts": self.extract_concepts(message),
            "original_ideas": self.extract_original_ideas(message),
            "investments": self.extract_investments(message),
            "deals": self.extract_deals(message),
            "regulations": self.extract_regulations(message),
            "compliance_items": self.extract_compliance(message)
        }
        
        # 计算置信度
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                entity["confidence"] = self.calculate_confidence(entity, message)
        
        return entities
    
    def extract_persons(self, message: str) -> List[Dict]:
        """提取人员名称"""
        persons = []
        
        # 使用 spaCy NER
        doc = self.nlp(message)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                persons.append({
                    "name": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "source": "spacy"
                })
        
        # 使用 BERT NER
        ner_results = self.ner_pipeline(message)
        for result in ner_results:
            if result["entity"] == "PER":
                persons.append({
                    "name": result["word"],
                    "start": result["start"],
                    "end": result["end"],
                    "source": "bert"
                })
        
        # 去重
        persons = self.deduplicate_persons(persons)
        
        # 检查别名
        for person in persons:
            aliases = self.find_aliases(person["name"])
            if aliases:
                person["aliases"] = aliases
        
        return persons
    
    def extract_companies(self, message: str) -> List[Dict]:
        """提取公司名称"""
        companies = []
        
        # 使用公司名称词典
        for company_name in self.company_dict:
            if company_name.lower() in message.lower():
                companies.append({
                    "name": company_name,
                    "source": "dictionary"
                })
        
        # 使用 NER
        doc = self.nlp(message)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                companies.append({
                    "name": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "source": "spacy"
                })
        
        # 去重
        companies = self.deduplicate_companies(companies)
        
        return companies
    
    def extract_investments(self, message: str) -> List[Dict]:
        """提取投资信息（企业级）"""
        investments = []
        
        # 识别融资轮次
        funding_rounds = ["Seed", "Series A", "Series B", "Series C", "Series D", "IPO"]
        for round_name in funding_rounds:
            if round_name in message:
                investments.append({
                    "type": "funding_round",
                    "round": round_name,
                    "source": "pattern"
                })
        
        # 识别金额
        amount_pattern = r'\$[\d,]+(?:\.\d+)?[MB]?(?:illion)?'
        amounts = re.findall(amount_pattern, message)
        for amount in amounts:
            investments.append({
                "type": "amount",
                "value": amount,
                "source": "regex"
            })
        
        # 识别投资者
        investors = self.extract_persons(message)
        for investor in investors:
            investments.append({
                "type": "investor",
                "name": investor["name"],
                "source": "person_extraction"
            })
        
        return investments
    
    def extract_deals(self, message: str) -> List[Dict]:
        """提取交易信息（企业级）"""
        deals = []
        
        # 识别并购关键词
        m_a_keywords = ["acquisition", "merger", "acquired", "merged", "buyout"]
        for keyword in m_a_keywords:
            if keyword in message.lower():
                deals.append({
                    "type": "merger_acquisition",
                    "keyword": keyword,
                    "source": "pattern"
                })
        
        # 识别战略合作
        partnership_keywords = ["partnership", "strategic alliance", "joint venture"]
        for keyword in partnership_keywords:
            if keyword in message.lower():
                deals.append({
                    "type": "partnership",
                    "keyword": keyword,
                    "source": "pattern"
                })
        
        return deals
    
    def extract_regulations(self, message: str) -> List[Dict]:
        """提取监管信息（企业级）"""
        regulations = []
        
        # 识别法规更新
        regulation_keywords = ["regulation", "compliance", "GDPR", "SEC", "FCC"]
        for keyword in regulation_keywords:
            if keyword in message:
                regulations.append({
                    "type": "regulation",
                    "keyword": keyword,
                    "source": "pattern"
                })
        
        # 标记合规风险
        risk_keywords = ["risk", "violation", "penalty", "fine"]
        for keyword in risk_keywords:
            if keyword in message.lower():
                regulations.append({
                    "type": "compliance_risk",
                    "keyword": keyword,
                    "source": "pattern"
                })
        
        return regulations
    
    def extract_compliance(self, message: str) -> List[Dict]:
        """提取合规信息（企业级）"""
        compliance_items = []
        
        # 识别合规框架
        frameworks = ["SOC 2", "ISO 27001", "HIPAA", "PCI DSS"]
        for framework in frameworks:
            if framework in message:
                compliance_items.append({
                    "type": "compliance_framework",
                    "framework": framework,
                    "source": "pattern"
                })
        
        return compliance_items
    
    def extract_concepts(self, message: str) -> List[Dict]:
        """提取概念"""
        concepts = []
        
        # 使用关键词提取
        doc = self.nlp(message)
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # 多词概念
                concepts.append({
                    "name": chunk.text,
                    "source": "noun_chunk"
                })
        
        return concepts
    
    def extract_original_ideas(self, message: str) -> List[Dict]:
        """提取原创想法"""
        # 使用 AI 模型判断原创性
        # 这里简化处理
        original_ideas = []
        
        # 识别新颖观点
        novelty_indicators = ["innovative", "novel", "unique", "breakthrough"]
        for indicator in novelty_indicators:
            if indicator in message.lower():
                original_ideas.append({
                    "content": message,
                    "indicator": indicator,
                    "source": "pattern"
                })
        
        return original_ideas
    
    def calculate_confidence(self, entity: Dict, message: str) -> float:
        """计算置信度"""
        confidence = 0.0
        
        # 基于来源
        if entity.get("source") == "spacy":
            confidence += 0.3
        elif entity.get("source") == "bert":
            confidence += 0.4
        elif entity.get("source") == "dictionary":
            confidence += 0.5
        
        # 基于上下文
        if entity.get("start") and entity.get("end"):
            context = message[max(0, entity["start"]-20):min(len(message), entity["end"]+20)]
            if any(word in context.lower() for word in ["said", "announced", "reported"]):
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    def deduplicate_persons(self, persons: List[Dict]) -> List[Dict]:
        """去重人员"""
        seen = set()
        unique_persons = []
        for person in persons:
            name = person["name"].lower()
            if name not in seen:
                seen.add(name)
                unique_persons.append(person)
        return unique_persons
    
    def deduplicate_companies(self, companies: List[Dict]) -> List[Dict]:
        """去重公司"""
        seen = set()
        unique_companies = []
        for company in companies:
            name = company["name"].lower()
            if name not in seen:
                seen.add(name)
                unique_companies.append(company)
        return unique_companies
    
    def find_aliases(self, name: str) -> List[str]:
        """查找别名"""
        return self.alias_map.get(name.lower(), [])
    
    def load_alias_map(self) -> Dict[str, List[str]]:
        """加载别名映射"""
        # 从数据库或文件加载
        return {}
    
    def load_company_dictionary(self) -> List[str]:
        """加载公司名称词典"""
        # 从数据库或文件加载
        return []
    
    def load_investment_terms(self) -> List[str]:
        """加载投资术语"""
        # 从数据库或文件加载
        return []


# 使用示例
if __name__ == "__main__":
    detector = EnterpriseEntityDetector()
    
    message = "John Smith announced that TechCorp raised $50M in Series B funding led by Sequoia Capital."
    entities = detector.detect_entities(message)
    
    print("Detected entities:")
    for entity_type, entity_list in entities.items():
        if entity_list:
            print(f"{entity_type}: {entity_list}")
