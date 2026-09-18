"""Astrological knowledge base (from sistema_enhanced merge source)."""
from __future__ import annotations

PLANETS = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]

RULERS = {
    "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
    "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
    "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"
}
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

class AstrologicalKnowledge:
    """Comprehensive astrological knowledge base for interpretations."""
    
    SIGN_DESCRIPTIONS = {
        "Aries": {
            "symbol": "♈",
            "element": "Fire",
            "quality": "Cardinal",
            "ruling_planet": "Mars",
            "keywords": ["Initiative", "Courage", "Leadership", "Independence", "Action"],
            "short_description": "The pioneering warrior who initiates new beginnings with bold enthusiasm.",
            "full_description": """Aries, the first sign of the zodiac, represents pure life force and the spark of 
individuality. Symbolized by the Ram, Aries embodies raw energy, pioneering spirit, and the drive to assert one's 
existence in the world. As a Cardinal Fire sign ruled by Mars, it combines initiatory power with passionate intensity 
to charge forward into new territory without hesitation.

The Aries archetype is that of the warrior, pioneer, and entrepreneur. This sign governs self-assertion, independence, 
courage, and the instinct to compete and conquer. Aries energy is direct, honest, and unapologetically self-focused. 
These individuals excel at starting projects, leading charges, and facing challenges head-on. They possess natural 
leadership abilities and thrive on competition, adventure, and physical activity.

In personality, Aries manifests as boldness, enthusiasm, and quick action. These individuals are often charismatic 
leaders who inspire others with their confidence and willingness to take risks. They excel in careers requiring 
initiative, such as entrepreneurship, athletics, or emergency response. Aries natives are straightforward 
communicators who value honesty and directness in relationships.

However, this pioneering energy creates challenges. The shadow side of Aries includes impulsiveness, impatience, 
self-centeredness, and difficulty completing what they've started. These individuals may rush into situations 
without considering consequences, leading to unnecessary conflicts or abandoned projects. Their competitive nature 
can become aggressive or domineering if unchecked. Aries may struggle with collaboration, preferring to go it alone 
rather than compromise. The spiritual lessons of Aries involve channeling raw energy constructively, learning 
patience and consideration for others, and understanding that true courage includes vulnerability and cooperation.""",
            "positive_traits": ["Courageous", "Energetic", "Honest", "Passionate", "Optimistic", "Adventurous"],
            "challenging_traits": ["Impulsive", "Impatient", "Self-centered", "Aggressive", "Reckless"],
            "body_parts": ["Head", "Face", "Eyes"],
            "career_paths": ["Entrepreneurship", "Sports", "Military", "Sales", "Leadership Roles"],
            "life_lessons": ["Patience", "Cooperation", "Follow-through", "Diplomacy", "Self-awareness"]
        },
        "Taurus": {
            "symbol": "♉",
            "element": "Earth",
            "quality": "Fixed",
            "ruling_planet": "Venus",
            "keywords": ["Stability", "Sensuality", "Persistence", "Security", "Practicality"],
            "short_description": "The steadfast builder who creates lasting value through patient determination.",
            "full_description": """Taurus, the second sign, represents the stabilization of individual existence through 
material security and sensory appreciation. Symbolized by the Bull, Taurus embodies earthly strength, persistence, 
and the drive to build and maintain resources. As a Fixed Earth sign ruled by Venus, it combines grounded stability 
with aesthetic appreciation to create lasting beauty and security.

The Taurus archetype is that of the builder, gardener, and sensualist. This sign governs material resources, values, 
physical pleasures, and the instinct to possess and preserve. Taurus energy is patient, reliable, and deeply connected 
to the physical world. These individuals excel at creating financial security, cultivating beauty, and enjoying life's 
sensual pleasures. They possess natural talents in finance, arts, or any field requiring persistence and practical skills.

In personality, Taurus manifests as reliability, sensuality, and determined focus. These individuals are often calm 
and composed, with a strong appreciation for comfort, good food, and beautiful surroundings. They excel in careers 
involving finance, real estate, arts, or agriculture. Taurus natives are loyal partners who value stability and 
physical affection in relationships.

However, this stabilizing energy creates challenges. The shadow side of Taurus includes stubbornness, possessiveness, 
materialism, and resistance to change. These individuals may cling to comfort zones, relationships, or possessions 
long after they've outlived their usefulness. Their love of security can become fear of loss, leading to hoarding 
or jealousy. Taurus may struggle with flexibility, preferring routine over innovation. The spiritual lessons of 
Taurus involve learning to release attachments, embracing change as part of growth, and understanding that true 
security comes from within rather than external possessions.""",
            "positive_traits": ["Reliable", "Patient", "Sensual", "Practical", "Loyal", "Determined"],
            "challenging_traits": ["Stubborn", "Possessive", "Materialistic", "Inflexible", "Indulgent"],
            "body_parts": ["Neck", "Throat", "Thyroid"],
            "career_paths": ["Finance", "Arts", "Agriculture", "Real Estate", "Culinary"],
            "life_lessons": ["Flexibility", "Non-attachment", "Sharing", "Adaptability", "Spiritual values"]
        },
        "Gemini": {
            "symbol": "♊",
            "element": "Air",
            "quality": "Mutable",
            "ruling_planet": "Mercury",
            "keywords": ["Communication", "Adaptability", "Curiosity", "Versatility", "Intellect"],
            "short_description": "The clever communicator who connects ideas and people with quick wit.",
            "full_description": """Gemini, the third sign, represents the development of perception and communication. 
Symbolized by the Twins, Gemini embodies duality, versatility, and the drive to connect and exchange information. As a 
Mutable Air sign ruled by Mercury, it combines intellectual flexibility with rapid mental processing to navigate the 
world through curiosity and adaptation.

The Gemini archetype is that of the messenger, networker, and eternal student. This sign governs communication, 
learning, short trips, siblings, and immediate environment. Gemini energy is quick-witted, adaptable, and socially 
agile. These individuals excel at multitasking, learning new skills, and connecting people and ideas. They possess 
natural talents in writing, speaking, teaching, or any field requiring mental agility and social interaction.

In personality, Gemini manifests as curiosity, wit, and social charm. These individuals are often engaging 
conversationalists with broad knowledge across many subjects. They excel in careers involving media, education, 
sales, or technology. Gemini natives are playful partners who value mental stimulation and variety in relationships.

However, this versatile energy creates challenges. The shadow side of Gemini includes superficiality, inconsistency, 
nervousness, and difficulty with depth or commitment. These individuals may scatter their energy across too many 
interests, leading to unfinished projects or shallow relationships. Their adaptability can become duplicity or 
manipulation. Gemini may struggle with focus, becoming restless or bored easily. The spiritual lessons of Gemini 
involve developing depth alongside breadth, learning to commit without losing freedom, and using communication for 
truth rather than evasion.""",
            "positive_traits": ["Adaptable", "Witty", "Curious", "Versatile", "Sociable", "Intelligent"],
            "challenging_traits": ["Superficial", "Inconsistent", "Nervous", "Gossipy", "Restless"],
            "body_parts": ["Arms", "Hands", "Lungs", "Nervous System"],
            "career_paths": ["Writing", "Teaching", "Journalism", "Sales", "Technology"],
            "life_lessons": ["Depth", "Commitment", "Focus", "Authenticity", "Emotional integration"]
        },
        "Cancer": {
            "symbol": "♋",
            "element": "Water",
            "quality": "Cardinal",
            "ruling_planet": "Moon",
            "keywords": ["Nurturing", "Emotional", "Protective", "Intuitive", "Home-loving"],
            "short_description": "The nurturing protector who creates emotional security through caring bonds.",
            "full_description": """Cancer, the fourth sign, represents the foundation of emotional security and belonging. 
Symbolized by the Crab, Cancer embodies protective instinct, emotional depth, and the drive to nurture and be nurtured. 
As a Cardinal Water sign ruled by the Moon, it combines initiatory energy with fluid emotional sensitivity to create 
safe havens and family bonds.

The Cancer archetype is that of the mother, nurturer, and guardian. This sign governs home, family, emotional needs, 
and ancestral roots. Cancer energy is intuitive, empathetic, and deeply protective of loved ones. These individuals 
excel at creating comfortable environments, providing emotional support, and preserving traditions. They possess 
natural talents in caregiving, real estate, food service, or any field involving nurturing or protection.

In personality, Cancer manifests as sensitivity, intuition, and strong family orientation. These individuals are often 
empathetic listeners with strong emotional intelligence. They excel in careers involving care, history, or home-related 
fields. Cancer natives are devoted partners who value emotional connection and security in relationships.

However, this protective energy creates challenges. The shadow side of Cancer includes moodiness, clinginess, 
indirectness, and difficulty letting go. These individuals may retreat into their shell when hurt, or use emotional 
manipulation to maintain security. Their sensitivity can become oversensitivity or paranoia. Cancer may struggle with 
boundaries, becoming overly dependent or controlling in relationships. The spiritual lessons of Cancer involve 
developing emotional independence, learning to release the past, and extending nurturing beyond immediate family to 
the larger world.""",
            "positive_traits": ["Nurturing", "Intuitive", "Loyal", "Protective", "Imaginative", "Empathetic"],
            "challenging_traits": ["Moody", "Clingy", "Indirect", "Oversensitive", "Manipulative"],
            "body_parts": ["Chest", "Breasts", "Stomach"],
            "career_paths": ["Nursing", "Teaching", "Real Estate", "Food Service", "Counseling"],
            "life_lessons": ["Independence", "Release", "Boundaries", "Objectivity", "Global care"]
        },
        "Leo": {
            "symbol": "♌",
            "element": "Fire",
            "quality": "Fixed",
            "ruling_planet": "Sun",
            "keywords": ["Creative", "Generous", "Dramatic", "Proud", "Leadership"],
            "short_description": "The radiant performer who inspires through creative self-expression and warmth.",
            "full_description": """Leo, the fifth sign, represents the development of creative self-expression and 
individual radiance. Symbolized by the Lion, Leo embodies regal presence, generosity, and the drive to shine and be 
appreciated. As a Fixed Fire sign ruled by the Sun, it combines sustained passion with vital life force to create 
and lead with heart-centered authority.

The Leo archetype is that of the king/queen, performer, and creative artist. This sign governs creativity, romance, 
children, and self-expression. Leo energy is warm, charismatic, and naturally authoritative. These individuals excel 
at inspiring others, creative pursuits, and leadership roles that allow them to shine. They possess natural talents 
in performing arts, teaching, or any field requiring charisma and creativity.

In personality, Leo manifests as confidence, generosity, and dramatic flair. These individuals are often natural 
leaders with a strong presence and warm heart. They excel in careers involving entertainment, education, or management. 
Leo natives are passionate partners who value romance, loyalty, and admiration in relationships.

However, this radiant energy creates challenges. The shadow side of Leo includes arrogance, attention-seeking, 
drama-queening, and difficulty sharing the spotlight. These individuals may become tyrannical or overly dramatic 
when insecure. Their pride can prevent them from admitting mistakes or accepting help. Leo may struggle with 
humility, becoming vain or self-centered. The spiritual lessons of Leo involve learning that true leadership serves 
others, developing humility alongside confidence, and recognizing that everyone's light deserves to shine.""",
            "positive_traits": ["Generous", "Creative", "Warm-hearted", "Confident", "Loyal", "Enthusiastic"],
            "challenging_traits": ["Arrogant", "Attention-seeking", "Dramatic", "Stubborn", "Bossy"],
            "body_parts": ["Heart", "Spine", "Upper Back"],
            "career_paths": ["Acting", "Teaching", "Politics", "Design", "Entertainment"],
            "life_lessons": ["Humility", "Service", "Sharing spotlight", "Authenticity", "Inner validation"]
        },
        "Virgo": {
            "symbol": "♍",
            "element": "Earth",
            "quality": "Mutable",
            "ruling_planet": "Mercury",
            "keywords": ["Analytical", "Practical", "Service-oriented", "Detail-focused", "Efficient"],
            "short_description": "The meticulous analyst who perfects through dedicated service and discernment.",
            "full_description": """Virgo, the sixth sign, represents the organization and refinement of daily life. 
Symbolized by the Virgin, Virgo embodies purity, service, and the drive to analyze and improve. As a Mutable Earth 
sign ruled by Mercury, it combines practical adaptability with analytical intelligence to perfect systems and serve 
others effectively.

The Virgo archetype is that of the craftsman, healer, and analyst. This sign governs work, health, service, and daily 
routines. Virgo energy is detail-oriented, efficient, and dedicated to improvement. These individuals excel at 
organization, problem-solving, and helping others through practical means. They possess natural talents in healthcare, 
editing, research, or any field requiring precision and analysis.

In personality, Virgo manifests as modesty, diligence, and helpfulness. These individuals are often intelligent 
problem-solvers with strong work ethic. They excel in careers involving service, health, or technical skills. Virgo 
natives are reliable partners who show love through practical acts of service.

However, this refining energy creates challenges. The shadow side of Virgo includes criticism, perfectionism, 
worry, and over-analysis. These individuals may become hyper-critical of self and others, leading to anxiety or 
dissatisfaction. Their helpfulness can become meddling or controlling. Virgo may struggle with self-acceptance, 
focusing on flaws rather than wholeness. The spiritual lessons of Virgo involve learning that perfection is an 
illusion, developing compassion alongside discernment, and understanding that true service includes self-care.""",
            "positive_traits": ["Analytical", "Helpful", "Precise", "Reliable", "Intelligent", "Modest"],
            "challenging_traits": ["Critical", "Perfectionist", "Worrying", "Fussy", "Overly cautious"],
            "body_parts": ["Intestines", "Digestive System", "Nervous System"],
            "career_paths": ["Healthcare", "Editing", "Research", "Accounting", "Teaching"],
            "life_lessons": ["Acceptance", "Compassion", "Wholeness", "Self-care", "Flexibility"]
        },
        "Libra": {
            "symbol": "♎",
            "element": "Air",
            "quality": "Cardinal",
            "ruling_planet": "Venus",
            "keywords": ["Harmonious", "Diplomatic", "Social", "Artistic", "Balanced"],
            "short_description": "The gracious diplomat who creates harmony through partnership and aesthetics.",
            "full_description": """Libra, the seventh sign, represents the awareness of others and the drive for balance. 
Symbolized by the Scales, Libra embodies harmony, partnership, and the pursuit of justice and beauty. As a Cardinal 
Air sign ruled by Venus, it combines initiatory social energy with aesthetic refinement to create balanced relationships 
and environments.

The Libra archetype is that of the diplomat, artist, and peacemaker. This sign governs partnerships, marriage, 
social harmony, and aesthetics. Libra energy is gracious, fair-minded, and relationship-oriented. These individuals 
excel at mediation, design, and creating social connections. They possess natural talents in law, arts, diplomacy, 
or any field requiring balance and aesthetics.

In personality, Libra manifests as charm, diplomacy, and artistic sensibility. These individuals are often elegant 
social butterflies with strong sense of fairness. They excel in careers involving law, design, or public relations. 
Libra natives are romantic partners who value equality and harmony in relationships.

However, this harmonizing energy creates challenges. The shadow side of Libra includes indecisiveness, people-pleasing, 
superficiality, and conflict avoidance. These individuals may compromise too much, losing themselves in relationships 
or becoming manipulative to maintain peace. Their love of beauty can become vanity or materialism. Libra may struggle 
with confrontation, preferring indirect approaches. The spiritual lessons of Libra involve developing inner balance 
independent of others, learning decisive action, and understanding that true harmony sometimes requires addressing 
conflict.""",
            "positive_traits": ["Diplomatic", "Charming", "Artistic", "Fair-minded", "Sociable", "Romantic"],
            "challenging_traits": ["Indecisive", "People-pleasing", "Superficial", "Avoidant", "Vain"],
            "body_parts": ["Kidneys", "Lower Back", "Skin"],
            "career_paths": ["Law", "Design", "Diplomacy", "Counseling", "Arts"],
            "life_lessons": ["Decisiveness", "Self-reliance", "Authenticity", "Confrontation", "Inner peace"]
        },
        "Scorpio": {
            "symbol": "♏",
            "element": "Water",
            "quality": "Fixed",
            "ruling_planet": "Pluto (modern), Mars (traditional)",
            "keywords": ["Intense", "Transformative", "Passionate", "Secretive", "Powerful"],
            "short_description": "The profound investigator who transforms through depth and intensity.",
            "full_description": """Scorpio, the eighth sign, represents the deepening of emotional bonds through 
transformation and shared resources. Symbolized by the Scorpion, Eagle, and Phoenix, Scorpio embodies intensity, 
regeneration, and the drive to penetrate life's mysteries. As a Fixed Water sign ruled by Pluto (modern) and Mars 
(traditional), it combines sustained emotional depth with penetrating power to catalyze profound change.

The Scorpio archetype is that of the detective, psychologist, and alchemist. This sign governs transformation, 
sexuality, shared resources, death, and rebirth. Scorpio energy is intense, perceptive, and magnetically powerful. 
These individuals excel at research, crisis management, and psychological insight. They possess natural talents in 
investigation, therapy, finance, or any field requiring depth and strategy.

In personality, Scorpio manifests as intensity, loyalty, and emotional depth. These individuals are often magnetic 
personalities with strong willpower and perceptive minds. They excel in careers involving research, psychology, 
or resource management. Scorpio natives are passionate partners who seek deep, transformative connections in 
relationships.

However, this transformative energy creates challenges. The shadow side of Scorpio includes jealousy, possessiveness, 
secretiveness, and power struggles. These individuals may become manipulative or vengeful when hurt, or obsess over 
control. Their intensity can become destructive or self-destructive. Scorpio may struggle with trust, leading to 
paranoia or isolation. The spiritual lessons of Scorpio involve learning to release control, forgive and let go, 
and use power for healing rather than domination.""",
            "positive_traits": ["Passionate", "Resourceful", "Loyal", "Perceptive", "Determined", "Transformative"],
            "challenging_traits": ["Jealous", "Secretive", "Manipulative", "Vengeful", "Obsessive"],
            "body_parts": ["Reproductive System", "Elimination Organs"],
            "career_paths": ["Psychology", "Investigation", "Finance", "Research", "Surgery"],
            "life_lessons": ["Trust", "Release", "Forgiveness", "Empowerment", "Healing"]
        },
        "Sagittarius": {
            "symbol": "♐",
            "element": "Fire",
            "quality": "Mutable",
            "ruling_planet": "Jupiter",
            "keywords": ["Optimistic", "Adventurous", "Philosophical", "Freedom-loving", "Expansive"],
            "short_description": "The wise explorer who seeks meaning through adventure and philosophy.",
            "full_description": """Sagittarius, the ninth sign, represents the expansion of consciousness through 
exploration and philosophy. Symbolized by the Centaur Archer, Sagittarius embodies the quest for truth, freedom, 
and higher meaning. As a Mutable Fire sign ruled by Jupiter, it combines adaptable enthusiasm with expansive optimism 
to pursue wisdom and growth.

The Sagittarius archetype is that of the philosopher, traveler, and teacher. This sign governs higher education, 
philosophy, long-distance travel, and belief systems. Sagittarius energy is optimistic, adventurous, and truth-seeking. 
These individuals excel at teaching, publishing, or any field involving exploration or big-picture thinking. They 
possess natural talents in sports, academia, or international relations.

In personality, Sagittarius manifests as enthusiasm, honesty, and philosophical bent. These individuals are often 
jovial adventurers with broad perspectives and love of freedom. They excel in careers involving travel, education, 
or law. Sagittarius natives are fun-loving partners who value independence and intellectual stimulation in relationships.

However, this expansive energy creates challenges. The shadow side of Sagittarius includes tactlessness, exaggeration, 
restlessness, and dogmatism. These individuals may become preachy or judgmental about beliefs, or avoid commitment 
through constant movement. Their optimism can become unrealistic or irresponsible. Sagittarius may struggle with 
details and routine. The spiritual lessons of Sagittarius involve developing tact alongside honesty, committing to 
depth in addition to breadth, and recognizing that truth is multifaceted.""",
            "positive_traits": ["Optimistic", "Honest", "Adventurous", "Generous", "Philosophical", "Enthusiastic"],
            "challenging_traits": ["Tactless", "Restless", "Irresponsible", "Dogmatic", "Exaggerating"],
            "body_parts": ["Hips", "Thighs", "Liver"],
            "career_paths": ["Teaching", "Travel", "Publishing", "Law", "Philosophy"],
            "life_lessons": ["Tact", "Commitment", "Realism", "Depth", "Tolerance"]
        },
        "Capricorn": {
            "symbol": "♑",
            "element": "Earth",
            "quality": "Cardinal",
            "ruling_planet": "Saturn",
            "keywords": ["Ambitious", "Disciplined", "Practical", "Responsible", "Patient"],
            "short_description": "The determined achiever who builds lasting structures through discipline.",
            "full_description": """Capricorn, the tenth sign, represents the structuring of society through achievement 
and responsibility. Symbolized by the Sea-Goat, Capricorn embodies ambition, discipline, and the drive to climb to 
the top through persistent effort. As a Cardinal Earth sign ruled by Saturn, it combines initiatory practicality with 
structured determination to build lasting legacies.

The Capricorn archetype is that of the executive, elder, and master builder. This sign governs career, public 
reputation, authority, and long-term goals. Capricorn energy is responsible, strategic, and achievement-oriented. 
These individuals excel at management, planning, and building organizations. They possess natural talents in business, 
politics, or any field requiring discipline and structure.

In personality, Capricorn manifests as ambition, reliability, and dry humor. These individuals are often mature 
beyond their years with strong sense of duty. They excel in careers involving management, finance, or government. 
Capricorn natives are committed partners who value stability and shared goals in relationships.

However, this structuring energy creates challenges. The shadow side of Capricorn includes pessimism, rigidity, 
workaholism, and emotional repression. These individuals may become overly controlling or status-conscious, sacrificing 
personal life for achievement. Their caution can become fear of failure. Capricorn may struggle with expressing 
emotions or enjoying the present moment. The spiritual lessons of Capricorn involve balancing ambition with emotional 
life, learning that vulnerability is strength, and understanding that true success includes inner fulfillment.""",
            "positive_traits": ["Ambitious", "Disciplined", "Responsible", "Patient", "Practical", "Loyal"],
            "challenging_traits": ["Pessimistic", "Rigid", "Workaholic", "Cold", "Controlling"],
            "body_parts": ["Bones", "Knees", "Skin"],
            "career_paths": ["Business", "Politics", "Engineering", "Management", "Finance"],
            "life_lessons": ["Emotional expression", "Joy", "Flexibility", "Inner worth", "Balance"]
        },
        "Aquarius": {
            "symbol": "♒",
            "element": "Air",
            "quality": "Fixed",
            "ruling_planet": "Uranus (modern), Saturn (traditional)",
            "keywords": ["Innovative", "Humanitarian", "Independent", "Intellectual", "Unconventional"],
            "short_description": "The visionary reformer who innovates for collective progress and freedom.",
            "full_description": """Aquarius, the eleventh sign, represents the innovation of society through progressive 
ideals and group consciousness. Symbolized by the Water Bearer, Aquarius embodies humanitarian vision, originality, 
and the drive to reform for the greater good. As a Fixed Air sign ruled by Uranus (modern) and Saturn (traditional), 
it combines sustained intellectual focus with revolutionary energy to create future-oriented change.

The Aquarius archetype is that of the inventor, rebel, and visionary. This sign governs innovation, groups, 
humanitarianism, and future visions. Aquarius energy is independent, progressive, and intellectually detached. 
These individuals excel at networking, invention, and social reform. They possess natural talents in technology, 
science, activism, or any field requiring innovative thinking.

In personality, Aquarius manifests as originality, humanitarianism, and intellectual independence. These individuals 
are often eccentric thinkers with strong social ideals. They excel in careers involving technology, science, or 
social causes. Aquarius natives are freedom-loving partners who value friendship and intellectual equality in 
relationships.

However, this innovative energy creates challenges. The shadow side of Aquarius includes detachment, rebellion for 
its own sake, unpredictability, and intellectual arrogance. These individuals may become emotionally aloof or rigidly 
attached to ideas. Their independence can become isolation or contrariness. Aquarius may struggle with intimacy and 
emotional expression. The spiritual lessons of Aquarius involve balancing group focus with personal relationships, 
integrating heart with mind, and using innovation in service of genuine human needs.""",
            "positive_traits": ["Innovative", "Humanitarian", "Independent", "Intelligent", "Progressive", "Friendly"],
            "challenging_traits": ["Detached", "Unpredictable", "Stubborn", "Aloof", "Rebellious"],
            "body_parts": ["Ankles", "Circulatory System", "Nervous System"],
            "career_paths": ["Technology", "Science", "Activism", "Invention", "Aviation"],
            "life_lessons": ["Emotional connection", "Flexibility", "Intimacy", "Grounding", "Compassion"]
        },
        "Pisces": {
            "symbol": "♓",
            "element": "Water",
            "quality": "Mutable",
            "ruling_planet": "Neptune (modern), Jupiter (traditional)",
            "keywords": ["Compassionate", "Intuitive", "Artistic", "Spiritual", "Imaginative"],
            "short_description": "The mystical dreamer who connects through universal compassion and imagination.",
            "full_description": """Pisces, the twelfth and final sign, represents the dissolution of individual ego into 
universal consciousness. Symbolized by two Fish swimming in opposite directions, 
Pisces embodies the tension between spiritual and material worlds, between escape and engagement. Ruled by both 
Jupiter (traditional) and Neptune (modern), this sign combines faith and expansion with mystical dissolution and 
divine imagination.

The Pisces archetype is that of the mystic, artist, and universal lover. This sign governs spirituality, dreams, 
imagination, hidden realms, and collective unconscious. Pisces energy is empathic, intuitive, and boundaryless. 
These individuals can merge with others emotionally, channel creative inspiration from unseen realms, and sense 
the underlying unity of all existence. They possess natural healing abilities and profound compassion for suffering.

In personality, Pisces manifests as sensitivity, creativity, and spiritual inclination. These individuals are often 
artistic or musical, able to channel beauty from the collective unconscious. They excel in careers involving healing, 
art, spirituality, or service to those in need. Pisces natives are natural empaths who feel others' pain as their 
own and often sacrifice personal needs for others' welfare. They need regular retreat from harsh worldly realities 
to recharge in solitude, nature, or creative pursuits.

However, this boundaryless sensitivity creates significant challenges. The shadow side of Pisces includes escapism, 
victimhood, martyrdom, and confusion between fantasy and reality. These individuals may turn to substances, fantasy, 
or dissociation to escape painful realities. Their empathy can lead to poor boundaries - absorbing others' problems, 
enabling dysfunction, or losing themselves in relationships. Pisces may struggle with practical matters, becoming 
disorganized or impractical. The victim/savior dynamic is strong - they may attract or enable troubled people while 
neglecting self-care. Deception (of self or others) can be an issue, as Pisces sees what they wish were true rather 
than what is. The spiritual lessons of Pisces involve developing healthy boundaries, distinguishing compassion from 
enabling, grounding spiritual insights in practical reality, and learning that true transcendence includes rather 
than escapes from earthly existence.""",
            "positive_traits": ["Compassionate", "Intuitive", "Artistic", "Gentle", "Wise", "Spiritual", "Adaptable"],
            "challenging_traits": ["Escapist", "Overly trusting", "Martyr complex", "Impractical", "Victim mentality"],
            "body_parts": ["Feet", "Lymphatic system", "Immune system"],
            "career_paths": ["Arts", "Healing Professions", "Music", "Photography", "Charity Work", "Spirituality"],
            "life_lessons": ["Boundaries", "Discernment", "Practical grounding", "Self-care", "Reality testing"]
        }
    }
    
    PLANET_DESCRIPTIONS = {
        "Sun": {
            "symbol": "☉",
            "keywords": ["Identity", "Ego", "Vitality", "Purpose", "Consciousness"],
            "description": """The Sun represents core identity, conscious will, and life purpose. It symbolizes 
the central organizing principle of the personality - who you are at your essence. The Sun's sign, house, and 
aspects describe how you shine, where you seek to express yourself authentically, and what gives your life meaning 
and vitality. A well-integrated Sun manifests as confidence, creativity, and natural authority."""
        },
        "Moon": {
            "symbol": "☽",
            "keywords": ["Emotions", "Instincts", "Needs", "Memory", "Subconscious"],
            "description": """The Moon represents emotional nature, instinctive reactions, and deep psychological needs. 
It symbolizes the inner child, the mother archetype, and our relationship with nurturing and security. The Moon's 
placement describes what makes you feel safe and comfortable, how you process emotions, and your habitual responses 
to life. It governs memory, moods, and the subconscious patterns that influence behavior."""
        },
        "Mercury": {
            "symbol": "☿",
            "keywords": ["Communication", "Thinking", "Learning", "Connection", "Perception"],
            "description": """Mercury represents the rational mind, communication style, and how we process information. 
It governs learning, writing, speaking, and all forms of exchange. Mercury's placement describes mental patterns, 
communication preferences, and intellectual interests. It shows how you think, learn, and connect ideas."""
        },
        "Venus": {
            "symbol": "♀",
            "keywords": ["Love", "Beauty", "Values", "Pleasure", "Attraction"],
            "description": """Venus represents love, beauty, pleasure, and values. It governs attraction, aesthetics, 
relationships, and what we find pleasurable. Venus's placement describes how you give and receive affection, what 
you find beautiful, your artistic sensibilities, and your core values regarding relationships and resources."""
        },
        "Mars": {
            "symbol": "♂",
            "keywords": ["Action", "Desire", "Anger", "Drive", "Assertion"],
            "description": """Mars represents action, desire, and assertive energy. It governs sexuality, anger, 
competition, and how we pursue what we want. Mars's placement describes your fighting style, what motivates you 
to take action, how you express anger, and where you direct your physical and sexual energy."""
        },
        "Jupiter": {
            "symbol": "♃",
            "keywords": ["Expansion", "Growth", "Faith", "Abundance", "Wisdom"],
            "description": """Jupiter represents growth, expansion, and the principle of increase. It governs faith, 
optimism, higher learning, philosophy, and abundance. Jupiter's placement describes where you seek growth and 
meaning, your philosophical outlook, relationship with faith and luck, and areas of natural talent and opportunity."""
        },
        "Saturn": {
            "symbol": "♄",
            "keywords": ["Structure", "Discipline", "Limitation", "Maturity", "Authority"],
            "description": """Saturn represents structure, limitation, discipline, and maturity through challenge. 
It governs time, responsibility, authority, and lessons learned through experience. Saturn's placement describes 
where you face obstacles and fears, develop mastery through patience, and ultimately gain wisdom and authority."""
        },
        "Uranus": {
            "symbol": "♅",
            "keywords": ["Revolution", "Innovation", "Freedom", "Awakening", "Change"],
            "description": """Uranus represents sudden change, innovation, revolution, and awakening. It governs 
technology, progress, independence, and breakthrough experiences. Uranus's placement describes where you seek 
freedom and originality, rebel against convention, and experience sudden insights or disruptions."""
        },
        "Neptune": {
            "symbol": "♆",
            "keywords": ["Spirituality", "Illusion", "Compassion", "Transcendence", "Imagination"],
            "description": """Neptune represents spirituality, imagination, transcendence, and the dissolution of 
boundaries. It governs dreams, mysticism, compassion, and also illusion and confusion. Neptune's placement describes 
where you seek spiritual connection, may experience confusion or deception, and can access divine inspiration."""
        },
        "Pluto": {
            "symbol": "♇",
            "keywords": ["Transformation", "Power", "Regeneration", "Intensity", "Depth"],
            "description": """Pluto represents transformation, death and rebirth, and deep psychological processes. 
It governs power, intensity, sexuality, and profound change. Pluto's placement describes where you experience 
intense transformation, confront shadow material, and discover hidden sources of power and regeneration."""
        }
    }
    
    ASPECT_INTERPRETATIONS = {
        "Conjunction": {
            "angle": 0,
            "orb": 8,
            "nature": "Neutral/Intense",
            "description": """A conjunction merges the energies of two planets, creating a powerful blended influence. 
The planets function as a unit, each coloring the expression of the other. This is the most powerful aspect, 
representing new beginnings and concentrated energy. The nature depends on the planets involved - harmonious 
planets create easy conjunction, while challenging planets may create internal conflict."""
        },
        "Opposition": {
            "angle": 180,
            "orb": 8,
            "nature": "Dynamic/Challenging",
            "description": """An opposition creates tension between two planetary energies pulling in opposite 
directions. This aspect represents the need for balance and integration of polar opposite qualities. It often 
manifests as external conflicts or projection onto others until integration is achieved. The challenge is to 
honor both sides rather than swinging between extremes."""
        },
        "Trine": {
            "angle": 120,
            "orb": 7,
            "nature": "Harmonious/Flowing",
            "description": """A trine creates harmonious flow between planets in compatible elements. This aspect 
represents natural talent, ease, and support. Energy flows smoothly between the planetary principles, creating 
gifts and abilities. However, trines can also indicate laziness or taking things for granted, as the ease may 
prevent development of discipline."""
        },
        "Square": {
            "angle": 90,
            "orb": 6,
            "nature": "Dynamic/Challenging",
            "description": """A square creates friction and dynamic tension requiring action and adjustment. This 
aspect represents challenges that demand growth, effort, and problem-solving. While difficult, squares are often 
the most productive aspects, as they force development of skills and character. The key is to use the tension 
constructively rather than avoiding the challenge."""
        },
        "Sextile": {
            "angle": 60,
            "orb": 6,
            "nature": "Harmonious/Opportunistic",
            "description": """A sextile creates opportunities for cooperation between planets. Unlike trines, 
sextiles require some effort to activate. This aspect represents potential talents and opportunities that 
manifest when initiative is taken. It provides supportive connections that can be developed with conscious 
effort."""
        },
        "Quincunx": {
            "angle": 150,
            "orb": 3,
            "nature": "Adjustment/Awkward",
            "description": """A quincunx (or inconjunct) creates an awkward relationship between planets in signs 
with nothing in common. This aspect requires constant adjustment and adaptation. It often manifests as a feeling 
that two areas of life don't quite fit together, requiring creative solutions and ongoing compromise."""
        }
    }
    
    HOUSE_MEANINGS = {
        1: {
            "name": "First House (Ascendant)",
            "keywords": ["Self", "Identity", "Appearance", "First Impressions"],
            "description": """The First House represents self-image, physical appearance, and how others perceive 
you initially. It describes your approach to life, personal style, and the mask or persona you present to the 
world. Planets here significantly influence personality and life approach."""
        },
        2: {
            "name": "Second House",
            "keywords": ["Values", "Resources", "Money", "Self-Worth"],
            "description": """The Second House governs material resources, money, possessions, and personal values. 
It describes your relationship with material security, what you value, and how you earn and spend. It also relates 
to self-worth and innate talents."""
        },
        3: {
            "name": "Third House",
            "keywords": ["Communication", "Learning", "Siblings", "Short Trips"],
            "description": """The Third House rules communication, early learning, siblings, neighbors, and short 
trips. It describes your thinking style, communication patterns, relationship with siblings, and everyday interactions 
in your immediate environment."""
        },
        4: {
            "name": "Fourth House (IC)",
            "keywords": ["Home", "Family", "Roots", "Private Self"],
            "description": """The Fourth House represents home, family, roots, and emotional foundations. It describes 
your relationship with parents (especially mother/nurturing parent), your private self, sense of belonging, and 
what makes you feel secure. This is the most private sector of the chart."""
        },
        5: {
            "name": "Fifth House",
            "keywords": ["Creativity", "Romance", "Children", "Play"],
            "description": """The Fifth House governs creativity, self-expression, romance, children, and pleasure. 
It describes how you play, create, take risks, and express your unique self. It shows your approach to dating, 
hobbies, artistic pursuits, and relationship with children."""
        },
        6: {
            "name": "Sixth House",
            "keywords": ["Work", "Health", "Service", "Daily Routine"],
            "description": """The Sixth House rules daily work, health, service, and routines. It describes your 
work ethic, health habits, relationship with service and employment, and how you maintain daily life. It shows 
approaches to wellness and the mind-body connection."""
        },
        7: {
            "name": "Seventh House (Descendant)",
            "keywords": ["Partnership", "Marriage", "Others", "Projection"],
            "description": """The Seventh House represents partnerships, marriage, and one-to-one relationships. 
It describes what you seek in partners, how you relate in committed relationships, and qualities you may project 
onto others. This is the house of "the other" as mirror."""
        },
        8: {
            "name": "Eighth House",
            "keywords": ["Transformation", "Intimacy", "Shared Resources", "Death"],
            "description": """The Eighth House governs transformation, deep intimacy, shared resources, death, and 
rebirth. It describes your approach to deep bonding, sexuality, psychological work, crisis, and transformation. 
It also rules inheritances, taxes, and joint finances."""
        },
        9: {
            "name": "Ninth House",
            "keywords": ["Philosophy", "Travel", "Higher Education", "Belief"],
            "description": """The Ninth House rules higher education, philosophy, long-distance travel, and belief 
systems. It describes your quest for meaning, relationship with faith and spirituality, approach to learning, 
and connection with foreign cultures."""
        },
        10: {
            "name": "Tenth House (Midheaven)",
            "keywords": ["Career", "Reputation", "Achievement", "Public Life"],
            "description": """The Tenth House represents career, public reputation, achievement, and life direction. 
It describes your professional path, relationship with authority, public image, and major life accomplishments. 
This is the most public sector of the chart."""
        },
        11: {
            "name": "Eleventh House",
            "keywords": ["Friends", "Groups", "Aspirations", "Community"],
            "description": """The Eleventh House governs friendships, groups, social causes, and future aspirations. 
It describes your relationship with community, approach to friendship, social ideals, and hopes for the future. 
It shows where you find your tribe."""
        },
        12: {
            "name": "Twelfth House",
            "keywords": ["Spirituality", "Unconscious", "Solitude", "Transcendence"],
            "description": """The Twelfth House rules spirituality, the unconscious, hidden matters, and transcendence. 
It describes your inner spiritual life, relationship with solitude, unconscious patterns, and areas of life requiring 
surrender. It's the house of karma, mysticism, and dissolution of ego."""
        }
    }
    
    @classmethod
    def get_sign_interpretation(cls, sign_name, planet_name=None):
        """Get comprehensive interpretation for a planet in a sign."""
        if sign_name not in cls.SIGN_DESCRIPTIONS:
            return f"Interpretation for {sign_name} not available."
        
        sign_info = cls.SIGN_DESCRIPTIONS[sign_name]
        lines = []
        lines.append(f"\n{'='*80}")
        if planet_name:
            lines.append(f"{planet_name} in {sign_name} {sign_info['symbol']}")
        else:
            lines.append(f"{sign_name} {sign_info['symbol']}")
        lines.append(f"{'='*80}")
        lines.append(f"Element: {sign_info['element']} | Quality: {sign_info['quality']} | Ruler: {sign_info['ruling_planet']}")
        lines.append(f"Keywords: {', '.join(sign_info['keywords'])}")
        lines.append(f"\n{sign_info['short_description']}")
        lines.append(f"\n{sign_info['full_description']}")
        lines.append(f"\nPositive Traits: {', '.join(sign_info['positive_traits'])}")
        lines.append(f"\nChallenging Traits: {', '.join(sign_info['challenging_traits'])}")
        lines.append(f"\nGoverns: {', '.join(sign_info['body_parts'])}")
        lines.append(f"\nCareer Paths: {', '.join(sign_info['career_paths'])}")
        lines.append(f"\nLife Lessons: {', '.join(sign_info['life_lessons'])}")
        
        return "\n".join(lines)
    
    @classmethod
    def get_planet_interpretation(cls, planet_name):
        """Get interpretation for a planet's general meaning."""
        if planet_name not in cls.PLANET_DESCRIPTIONS:
            return f"Interpretation for {planet_name} not available."
        
        planet_info = cls.PLANET_DESCRIPTIONS[planet_name]
        lines = []
        lines.append(f"\n{planet_name} {planet_info['symbol']}")
        lines.append(f"Keywords: {', '.join(planet_info['keywords'])}")
        lines.append(f"{planet_info['description']}")
        return "\n".join(lines)
    
    @classmethod
    def get_aspect_interpretation(cls, aspect_name, planet1, planet2):
        """Get interpretation for an aspect between two planets."""
        if aspect_name not in cls.ASPECT_INTERPRETATIONS:
            return f"Interpretation for {aspect_name} not available."
        
        aspect_info = cls.ASPECT_INTERPRETATIONS[aspect_name]
        lines = []
        lines.append(f"\n{planet1} {aspect_name} {planet2}")
        lines.append(f"Nature: {aspect_info['nature']} | Orb: {aspect_info['orb']}°")
        lines.append(f"{aspect_info['description']}")
        return "\n".join(lines)
    
    @classmethod
    def get_house_interpretation(cls, house_num):
        """Get interpretation for a house."""
        if house_num not in cls.HOUSE_MEANINGS:
            return f"Interpretation for House {house_num} not available."
        
        house_info = cls.HOUSE_MEANINGS[house_num]
        lines = []
        lines.append(f"\n{house_info['name']}")
        lines.append(f"Keywords: {', '.join(house_info['keywords'])}")
        lines.append(f"{house_info['description']}")
        return "\n".join(lines)

