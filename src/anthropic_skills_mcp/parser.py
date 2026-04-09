import os
import yaml
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

# Configure logging to stderr for stdio transport compatibility
logger = logging.getLogger(__name__)

@dataclass
class Skill:
    name: str
    description: str
    content: str
    frontmatter: Dict[str, any]

def parse_skill_file(file_path: str) -> Optional[Skill]:
    """Parses a SKILL.md file and extracts YAML frontmatter and content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines or not lines[0].strip() == "---":
            logger.error(f"Skill file {file_path} missing leading '---'")
            return None
        
        # Find closing ---
        try:
            closing_index = -1
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    closing_index = i
                    break
            
            if closing_index == -1:
                logger.error(f"Skill file {file_path} missing closing '---'")
                return None
            
            frontmatter_raw = "".join(lines[1:closing_index])
            content = "".join(lines[closing_index+1:])
            
            frontmatter = yaml.safe_load(frontmatter_raw)
            
            if not isinstance(frontmatter, dict):
                logger.error(f"Skill file {file_path} frontmatter is not a dictionary")
                return None
            
            name = frontmatter.get("name")
            description = frontmatter.get("description")
            
            if not name or not description:
                logger.error(f"Skill file {file_path} missing 'name' or 'description' in frontmatter")
                return None
            
            return Skill(
                name=name,
                description=description,
                content=content,
                frontmatter=frontmatter
            )
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML in {file_path}: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error reading skill file {file_path}: {e}")
        return None

def load_skills(skills_dir: str) -> Dict[str, Skill]:
    """Recursively loads all SKILL.md files from the specified directory."""
    skills = {}
    
    if not os.path.isdir(skills_dir):
        logger.error(f"Skills directory {skills_dir} does not exist or is not a directory")
        return skills
    
    for root, _, files in os.walk(skills_dir):
        for file in files:
            if file == "SKILL.md":
                full_path = os.path.join(root, file)
                skill = parse_skill_file(full_path)
                if skill:
                    if skill.name in skills:
                        logger.warning(f"Duplicate skill name '{skill.name}' found at {full_path}. Skipping.")
                        continue
                    skills[skill.name] = skill
    
    return skills
