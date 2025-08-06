"""
Biology Subject Configuration
Specialized configuration for biology courses
"""
from typing import Dict, List
from .generic_config import GenericConfig

class BiologyConfig(GenericConfig):
    """
    Biology-specific configuration
    Inherits from GenericConfig and overrides with biology-specific content
    """
    
    @staticmethod
    def get_subject_info() -> Dict[str, str]:
        """Return biology subject information"""
        return {
            'name': 'biology',
            'display_name': 'Biology',
            'description': 'Biology course assistant specializing in life sciences',
            'version': '1.0'
        }
    
    @staticmethod
    def get_system_prompt() -> str:
        """Return biology-specific system prompt"""
        return """You are a helpful biology tutor assistant. Use the provided course content to answer the student's question accurately and clearly.

Guidelines:
- Base your answer primarily on the provided course content
- Be educational and explain biological concepts clearly
- Use proper biological terminology while keeping explanations accessible
- Include molecular, cellular, and organismal perspectives when relevant
- Connect concepts to real-world biological examples
- If the content doesn't fully answer the question, say so
- Keep answers concise but thorough
- Use bullet points or numbered lists when helpful for clarity"""
    
    @staticmethod
    def get_topic_keywords() -> Dict[str, List[str]]:
        """Return biology-specific topic keywords"""
        base_keywords = GenericConfig.get_topic_keywords()
        
        # Add biology-specific keywords
        biology_keywords = {
            'photosynthesis': ['Calvin cycle', 'light reactions', 'chloroplasts', 'ATP synthesis'],
            'dna': ['replication', 'transcription', 'translation', 'central dogma'],
            'protein': ['amino acids', 'protein folding', 'enzymes', 'protein structure'],
            'cell': ['organelles', 'membrane', 'nucleus', 'cytoplasm'],
            'membrane': ['transport', 'diffusion', 'osmosis', 'membrane proteins'],
            'enzyme': ['catalysis', 'activation energy', 'enzyme kinetics', 'allosteric regulation'],
            'lac operon': ['gene regulation', 'transcription', 'operons', 'bacterial genetics'],
            'evolution': ['natural selection', 'adaptation', 'speciation', 'phylogeny'],
            'ecology': ['ecosystem', 'food chain', 'biodiversity', 'population'],
            'genetics': ['alleles', 'inheritance', 'mutation', 'genotype', 'phenotype'],
            'metabolism': ['glycolysis', 'respiration', 'fermentation', 'ATP'],
            'anatomy': ['organs', 'tissues', 'systems', 'physiology'],
            'molecular biology': ['DNA', 'RNA', 'proteins', 'biochemistry']
        }
        
        # Merge with base keywords
        base_keywords.update(biology_keywords)
        return base_keywords
    
    @staticmethod
    def detect_subject_keywords() -> List[str]:
        """Return keywords that indicate biology content"""
        return [
            # Core biology terms
            'biology', 'biological', 'organism', 'cell', 'cellular',
            'molecular', 'genetics', 'evolution', 'ecology', 'anatomy',
            'physiology', 'biochemistry', 'metabolism', 'photosynthesis',
            
            # Molecules and structures
            'dna', 'rna', 'protein', 'enzyme', 'amino acid', 'nucleotide',
            'chromosome', 'gene', 'allele', 'membrane', 'organelle',
            
            # Processes
            'transcription', 'translation', 'replication', 'respiration',
            'fermentation', 'mitosis', 'meiosis', 'diffusion', 'osmosis',
            
            # Organisms and systems
            'bacteria', 'virus', 'plant', 'animal', 'fungi', 'ecosystem',
            'species', 'population', 'tissue', 'organ', 'system'
        ]
    
    @staticmethod
    def get_welcome_message() -> str:
        """Return biology-specific welcome message"""
        return """
🧬 Welcome to your Biology Study Assistant!

I'm specialized in helping you understand biological concepts and processes.
I can assist with topics ranging from molecular biology to ecology.

My expertise includes:
• Cell biology and molecular processes
• Genetics and evolution
• Anatomy and physiology  
• Ecology and environmental biology
• Biochemistry and metabolism

Ask me about any biology topic from your coursework!
        """.strip()
    
    @staticmethod
    def get_question_types() -> List[str]:
        """Return biology-appropriate question types"""
        return [
            'definition',
            'process_explanation',
            'mechanism_description', 
            'comparison',
            'function_analysis',
            'experimental_design',
            'application',
            'system_interaction'
        ]
