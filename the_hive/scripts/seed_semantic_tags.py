"""Seed script for semantic tags with initial hierarchy.

SRS Requirements:
- FR-8.4: WikiData-inspired semantic tag system with hierarchies

Run this script to:
1. Add 'aliases' column to existing tags table (migration)
2. Seed initial tag hierarchy (e.g., gardening → lawn-mowing)
3. Create synonym relationships
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.core.db import engine
from app.models.tag import Tag
from app.models.semantic_tag import SemanticTagSynonym


def seed_semantic_tags():
    """Seed initial semantic tag hierarchy."""
    
    with Session(engine) as session:
        print("🌱 Seeding semantic tag hierarchy...")
        
        # Define initial tag hierarchy
        # Format: (name, description, aliases, parent_name)
        tag_data = [
            # Top-level categories
            ("physical-work", "Physical labor and hands-on tasks", "manual-labor,handiwork", None),
            ("digital-work", "Computer and internet-based tasks", "online-work,remote-work", None),
            ("creative-work", "Artistic and creative tasks", "arts,creativity", None),
            ("education", "Teaching and learning activities", "teaching,tutoring,learning", None),
            ("household", "Home maintenance and domestic tasks", "home,domestic", None),
            
            # Physical work subcategories
            ("gardening", "Garden and outdoor plant care", "lawn-care,landscaping", "physical-work"),
            ("lawn-mowing", "Cutting grass and lawn maintenance", "grass-cutting,mowing", "gardening"),
            ("pruning", "Trimming plants and trees", "tree-trimming,hedge-cutting", "gardening"),
            ("planting", "Planting seeds, flowers, and vegetables", "seeding,transplanting", "gardening"),
            
            ("construction", "Building and renovation work", "building,renovation", "physical-work"),
            ("carpentry", "Woodworking and furniture making", "woodwork", "construction"),
            ("painting", "Wall and surface painting", "decorating", "construction"),
            ("plumbing", "Pipe and water system work", "pipes,drainage", "construction"),
            ("electrical", "Electrical installations and repairs", "wiring,electrician", "construction"),
            
            ("moving", "Transportation and moving services", "transport,delivery", "physical-work"),
            
            # Digital work subcategories
            ("programming", "Software development and coding", "coding,software-development", "digital-work"),
            ("web-development", "Website creation and maintenance", "website,frontend,backend", "programming"),
            ("mobile-development", "Mobile app development", "app-development,ios,android", "programming"),
            ("python", "Python programming language", "python-programming", "programming"),
            ("javascript", "JavaScript programming language", "js,node", "programming"),
            ("react", "React JavaScript framework", "reactjs", "javascript"),
            
            ("design", "Graphic and visual design", "graphic-design,visual-design", "digital-work"),
            ("ui-design", "User interface design", "interface-design", "design"),
            ("logo-design", "Logo and branding design", "branding", "design"),
            
            ("data-entry", "Data input and management", "typing,data-management", "digital-work"),
            
            # Creative work subcategories
            ("writing", "Content and creative writing", "content-writing,copywriting", "creative-work"),
            ("music", "Musical performances and lessons", "singing,instruments", "creative-work"),
            ("photography", "Photo taking and editing", "photo,images", "creative-work"),
            ("video-editing", "Video production and editing", "videography", "creative-work"),
            
            # Education subcategories
            ("math-tutoring", "Mathematics teaching", "math,mathematics", "education"),
            ("language-tutoring", "Language teaching and practice", "languages,esl", "education"),
            ("english", "English language teaching", "esl,english-tutoring", "language-tutoring"),
            ("music-lessons", "Musical instrument lessons", "instrument-lessons", "education"),
            
            # Household subcategories
            ("cleaning", "House and space cleaning", "housekeeping", "household"),
            ("cooking", "Meal preparation and cooking", "meal-prep,baking", "household"),
            ("childcare", "Looking after children", "babysitting,nanny", "household"),
            ("pet-care", "Taking care of pets", "dog-walking,pet-sitting", "household"),
        ]
        
        # Create tags with hierarchy
        tag_map = {}  # name -> Tag object
        
        # First pass: create all tags
        for name, description, aliases, parent_name in tag_data:
            existing = session.exec(
                select(Tag).where(Tag.name == name)
            ).first()
            
            if existing:
                print(f"  ✓ Tag '{name}' already exists")
                tag_map[name] = existing
                # Update description and aliases if empty
                if not existing.description:
                    existing.description = description
                if not existing.aliases:
                    existing.aliases = aliases
                session.add(existing)
            else:
                tag = Tag(
                    name=name,
                    description=description,
                    aliases=aliases,
                    parent_id=None  # Set in second pass
                )
                session.add(tag)
                session.flush()  # Get ID
                tag_map[name] = tag
                print(f"  + Created tag '{name}'")
        
        session.commit()
        
        # Second pass: set parent relationships
        for name, description, aliases, parent_name in tag_data:
            if parent_name:
                tag = tag_map[name]
                parent = tag_map.get(parent_name)
                if parent and tag.parent_id != parent.id:
                    tag.parent_id = parent.id
                    session.add(tag)
                    print(f"  → Set '{name}' parent to '{parent_name}'")
        
        session.commit()
        
        # Create synonym relationships
        synonyms = [
            ("programming", "coding"),
            ("construction", "building"),
            ("gardening", "lawn-care"),
            ("web-development", "website"),
            ("python", "python-programming"),
            ("javascript", "js"),
        ]
        
        print("\n🔗 Creating synonym relationships...")
        for tag1_name, tag2_name in synonyms:
            tag1 = tag_map.get(tag1_name)
            tag2 = tag_map.get(tag2_name)
            
            if tag1 and tag2:
                # Check if relationship already exists
                existing = session.exec(
                    select(SemanticTagSynonym).where(
                        ((SemanticTagSynonym.tag_id == tag1.id) & (SemanticTagSynonym.synonym_id == tag2.id)) |
                        ((SemanticTagSynonym.tag_id == tag2.id) & (SemanticTagSynonym.synonym_id == tag1.id))
                    )
                ).first()
                
                if not existing:
                    syn = SemanticTagSynonym(tag_id=tag1.id, synonym_id=tag2.id)
                    session.add(syn)
                    print(f"  ↔ Linked '{tag1_name}' ↔ '{tag2_name}'")
                else:
                    print(f"  ✓ Synonym '{tag1_name}' ↔ '{tag2_name}' already exists")
        
        session.commit()
        
        print("\n✅ Semantic tag hierarchy seeded successfully!")
        print(f"   Total tags: {len(tag_map)}")
        print("\n📊 Tag hierarchy summary:")
        print("   - Physical work: gardening, construction, moving")
        print("   - Digital work: programming, design, data-entry")
        print("   - Creative work: writing, music, photography")
        print("   - Education: tutoring, music-lessons")
        print("   - Household: cleaning, cooking, childcare, pet-care")


if __name__ == "__main__":
    print("🚀 Starting semantic tag seeding...\n")
    seed_semantic_tags()
    print("\n🎉 Done!")
