---
name: prompt-expander
description: Expands simple, vague user webpage requests into detailed, professional AI prompts for a webpage cloning/generation tool. Use this skill whenever a user provides a short or casual description of a webpage they want to build — such as "I want a music website", "make me a travel agency page", "create a club homepage", or any other brief webpage request. This skill identifies the website type, infers the best industry-standard structure, and outputs a comprehensive, AI-ready prompt covering layout, visual style, content sections, interactions, and audience. Always trigger this skill before generating any webpage code when the user's input is vague, short, or non-technical.
---

# Prompt Expander — Webpage Generation

This skill transforms a user's simple webpage description into a detailed, structured prompt that produces high-quality, professional webpages from an AI model.

## Your Job

When a user says something like:
- "I want a music website with a black background"
- "Make me a travel agency page"
- "Build a homepage for my student club"

You must **NOT** generate the webpage immediately. Instead, follow the steps below to produce an expanded, professional prompt first, then use that prompt to generate the webpage.

---

## Step 1: Identify the Website Type

Classify the user's request into one of these categories (or infer the closest match):

| Type | Keywords | Reference Section |
|------|----------|-------------------|
| Media / Entertainment | music, video, podcast, streaming, radio | `## REF: Media` |
| Travel / Tourism | travel, trip, hotel, tour, destination, agency | `## REF: Travel` |
| Community / Organization | club, society, association, team, nonprofit, school | `## REF: Community` |
| E-commerce / Product | shop, store, product, buy, sell, marketplace | `## REF: Ecommerce` |
| Portfolio / Personal | portfolio, resume, personal, freelance, artist | `## REF: Portfolio` |
| Restaurant / Food | restaurant, cafe, food, menu, bakery, bar | `## REF: Food` |
| Corporate / Business | company, agency, startup, SaaS, consulting, firm | `## REF: Corporate` |
| Event / Landing Page | event, conference, launch, concert, festival | `## REF: Event` |
| Other / Unknown | anything that doesn't match the above | `## REF: Other` |

If the type is ambiguous, make a reasonable inference and state your assumption.

---

## Step 2: Read the Reference Section

Once you've identified the type, scroll to the corresponding `## REF:` section below. Each section contains:
- Industry-standard page sections for that type
- Common content patterns and features
- Typical UI conventions users expect

---

## Step 3: Extract User Preferences

From the user's original message, extract any explicit preferences:
- **Colors / Theme**: Did they mention colors, dark/light mode, any style words?
- **Specific Content**: Did they name specific items, people, brands, categories?
- **Mood / Audience**: Any hints about who this is for or the feeling they want?
- **Features**: Any specific functionality mentioned (booking, search, maps, etc.)?

If nothing is mentioned, apply sensible modern defaults for that website type.

---

## Step 4: Build the Expanded Prompt

Combine the reference section structure + user preferences into a full prompt using this template:

```
I want to create a [WEBSITE TYPE] webpage.

**Visual Style:**
- Overall aesthetic: [inferred from type + user preference]
- Color scheme: [specific colors, not just "dark theme"]
- Typography: [style direction — bold/elegant/playful/clean]
- Layout feel: [card-based / editorial / grid / immersive / etc.]
- Inspiration: [reference 1-2 well-known sites of similar type]

**Page Sections:** (in order, top to bottom)
1. [Section name] — [what it contains and its purpose]
2. [Section name] — [what it contains and its purpose]
3. [Section name] — [what it contains and its purpose]
... (continue for all relevant sections)

**Content Details:**
1. [Content category] — [specific examples, names, items relevant to this type]
2. [Content category] — [specific examples]
... (3-6 content categories with concrete examples)

**Key Features & Interactions:**
- [Feature 1 with specific behavior description]
- [Feature 2 with specific behavior description]
- [Navigation type and structure]
- Hover effects: [specific description]
- Responsive: mobile + desktop

**Audience & Tone:**
- Target audience: [who will visit this site]
- Emotional tone: [what feeling the page should convey]
- Call to action: [what you want visitors to do]
```

---

## Step 5: Output Format

Present the expanded prompt clearly to the user, then ask:

> "Does this capture what you're looking for? You can adjust any details before I generate the webpage."

Give the user a chance to refine before proceeding to generation. If they approve or say "looks good / go ahead", proceed to generate the webpage using the expanded prompt.

---

## Quality Rules

- **Never use vague language** like "nice colors" or "good layout" — always be specific
- **Always include real examples** — name actual artists, destinations, dishes, brands relevant to the context
- **Match industry conventions** — a travel site should feel like Airbnb/Booking, a music site like Spotify, etc.
- **Preserve user intent** — if the user said "black background", keep it; expand around it, don't replace it
- **Scale complexity to the request** — a simple club homepage needs fewer sections than a full e-commerce site

---
---

# REFERENCE LIBRARY
# Read only the section that matches the identified website type.

---

## REF: Media / Entertainment

### Standard Page Sections
1. **Hero / Now Playing Banner** — Featured artist, album, or trending track with full-width visual
2. **Featured Playlists** — Curated collections, editor picks, mood-based playlists
3. **Popular Artists** — Grid of artist cards with photo, name, genre tag
4. **New Releases** — Latest albums/singles with cover art and release date
5. **Genre / Category Browser** — Visual genre tiles (Pop, Rock, Jazz, Hip-Hop, Classical, etc.)
6. **Charts / Top Tracks** — Ranked list of most-played songs this week
7. **Radio / Stations** — Live or curated continuous play streams
8. **Recommended For You** — Personalized suggestions based on taste
9. **Persistent Bottom Player** — Track info, progress bar, controls (play/pause/skip/shuffle/repeat/volume)

### Content Patterns
- Artist cards: photo thumbnail, name, follower count, genre
- Track rows: album art, title, artist, duration, play button
- Playlist cards: cover image, title, track count, creator name
- Genre tiles: background color/image, genre name

### UI Conventions
- Dark theme is industry standard (Spotify model)
- Sidebar navigation: Home, Search, Library, Liked Songs, Podcasts
- Hover on cards reveals play button overlay
- Premium vs Free tier distinction with lock icons
- Green or vibrant accent color on dark background

### Example Inspirations
Spotify, Apple Music, Tidal, SoundCloud, YouTube Music

---

## REF: Travel / Tourism

### Standard Page Sections
1. **Hero with Search** — Full-screen destination photo + search bar (where to / dates / guests)
2. **Popular Destinations** — Card grid of top cities/countries with photo + price from
3. **Travel Categories** — Beaches, Mountains, Cities, Cultural, Adventure, Luxury
4. **Featured Tours / Packages** — Highlighted deals with itinerary summary, price, duration
5. **Why Choose Us** — Trust signals: years of experience, satisfied customers, safety rating
6. **Testimonials** — Customer reviews with star rating, photo, destination visited
7. **Travel Blog / Tips** — Articles on destinations, packing, local culture
8. **Newsletter Signup** — Offer discount code for subscribing
9. **Footer** — Contact, About, Terms, Social links

### Content Patterns
- Destination cards: full-bleed photo, city name, country, "from $X/night"
- Tour packages: image, tour name, duration, highlights list, price, Book Now CTA
- Testimonial: avatar, name, country flag, star rating, quote

### UI Conventions
- Light or warm-toned theme (trust and adventure feel)
- Hero search bar is the #1 above-the-fold element
- Strong CTAs: "Book Now", "Explore", "Get a Quote"
- Map integration hints (show destination on map)
- Mobile-first (most travel browsing is on phone)

### Example Inspirations
Airbnb, Booking.com, Expedia, GetYourGuide, Viator

---

## REF: Community / Organization

### Standard Page Sections
1. **Hero with Mission Statement** — Bold headline describing who you are + Join CTA
2. **About the Club** — Short history, values, what makes this group unique
3. **Activities / Events** — Upcoming events with date, time, location, description
4. **Members / Team** — Grid of member cards: photo, name, role/title
5. **Gallery** — Photo grid of past activities and events
6. **Achievements / Milestones** — Awards, competitions won, years active, member count
7. **Join Us** — Application form or contact info, membership benefits
8. **News / Announcements** — Recent updates, blog posts, notices
9. **Contact & Social** — Location, email, social media links

### Content Patterns
- Event card: date badge, event name, location, short description, RSVP button
- Member card: circular photo, name, position, social link
- Achievement badge: icon, title, year

### UI Conventions
- Warm, approachable colors (greens, blues, university brand colors)
- Community feel: real photos over illustrations
- Clear Join / Contact CTA in hero
- Mobile-friendly (members check on phones)

### Example Inspirations
University club pages, Meetup.com groups, nonprofit homepages

---

## REF: Ecommerce / Product

### Standard Page Sections
1. **Hero Banner** — Promotional offer, new collection, or bestseller spotlight
2. **Category Navigation** — Visual category tiles (Men, Women, Electronics, Sale, etc.)
3. **Featured / Bestselling Products** — Product card grid with image, name, price, rating
4. **Promotional Banner** — Sale announcement, free shipping threshold, limited offer
5. **New Arrivals** — Latest products with "New" badge
6. **Brand Story / Trust** — About the brand, sustainability, quality promise
7. **Customer Reviews** — Star ratings, review text, verified purchase badges
8. **Recommended / Recently Viewed** — Personalized product suggestions
9. **Footer** — Shipping policy, returns, FAQ, newsletter

### Content Patterns
- Product card: image, product name, price (original + sale), star rating, Add to Cart
- Category tile: background image, category name, Shop Now link
- Review: star rating, reviewer name, date, review text, product photo

### UI Conventions
- Clean, product-focused layout (white space is important)
- Sticky header with cart icon and item count
- Filter/sort sidebar for product listings
- Quick-add to cart on hover
- Clear pricing and discount display

### Example Inspirations
ASOS, Nike, Zara, Amazon, Shopify stores

---

## REF: Portfolio / Personal

### Standard Page Sections
1. **Hero / Introduction** — Name, title, one-line bio, and profile photo or visual identity
2. **About Me** — Longer bio, background, skills summary, personality
3. **Skills / Tech Stack** — Visual skill bars or icon grid of tools and technologies
4. **Projects / Work** — Featured project cards: screenshot, name, description, tech used, links
5. **Experience / Timeline** — Work history in chronological or visual timeline format
6. **Testimonials** — Quotes from colleagues, clients, or managers
7. **Awards / Recognition** — Certifications, competition wins, press mentions
8. **Contact** — Email form, social links (GitHub, LinkedIn, Dribbble, etc.)

### Content Patterns
- Project card: screenshot/mockup, project title, 1-2 sentence description, tech stack tags, Live/GitHub links
- Skill icon: tool logo + name + proficiency level
- Timeline item: date, company/role, bullet achievements

### UI Conventions
- Strong personal branding — color and font choice reflects personality
- Dark or light depending on field (developers often dark, designers often light/colorful)
- Minimal navigation — scroll-based single page common
- Prominent contact CTA

### Example Inspirations
Awwwards.com portfolio winners, Dribbble designer profiles, GitHub Pages portfolios

---

## REF: Food / Restaurant

### Standard Page Sections
1. **Hero with Atmosphere Photo** — Full-screen food/restaurant photo + tagline + Reserve/Order CTA
2. **About the Restaurant** — Story, chef, cuisine style, ambiance description
3. **Menu Highlights** — Featured dishes with photo, name, description, price
4. **Full Menu Categories** — Starters, Mains, Desserts, Drinks tabs
5. **Reservations** — Date/time/party size picker or OpenTable embed
6. **Gallery** — Food photography grid + interior/atmosphere shots
7. **Reviews** — Google/Yelp-style rating display, customer quotes
8. **Location & Hours** — Map embed, address, opening hours per day
9. **Order Online / Delivery** — Link to delivery platform or own ordering system

### Content Patterns
- Dish card: full-bleed photo, dish name, short description, dietary tags (V/GF/Spicy), price
- Menu tab: category name, list of dishes with name + description + price
- Review: star rating, platform logo, reviewer name, quote

### UI Conventions
- Warm, appetizing colors (oranges, creams, deep reds)
- Large, high-quality food photography is essential
- Clear reservation/order CTA above the fold
- Mobile-optimized menu (scrollable, easy to read)

### Example Inspirations
Nobu, Dishoom, The Fat Duck websites, local bistro sites on Squarespace

---

## REF: Corporate / Business

### Standard Page Sections
1. **Hero with Value Proposition** — Clear headline of what the company does + Get Started CTA
2. **Services / Products Overview** — Icon + title + short description cards for each offering
3. **How It Works** — 3-4 step process with numbered steps and icons
4. **Social Proof / Clients** — Logo wall of notable clients or partners
5. **Case Studies / Results** — Success stories with metrics (e.g., "increased revenue by 40%")
6. **Team / Leadership** — Key people with photo, name, title
7. **Pricing** (if applicable) — Tiered pricing cards with feature comparison
8. **Testimonials** — Client quotes with company, name, photo
9. **Blog / Resources** — Articles, whitepapers, guides
10. **Contact / CTA Footer** — "Let's Talk" form, office locations

### Content Patterns
- Service card: icon, service name, 2-3 sentence description
- Pricing card: tier name, price, feature list, CTA button (highlight recommended tier)
- Testimonial: quote, client name, company, headshot

### UI Conventions
- Professional, trustworthy aesthetic (blues, grays, whites)
- Clear information hierarchy — what you do, who you serve, why choose you
- Strong above-fold CTA (Book a Call, Get a Demo, Start Free Trial)
- Mobile-responsive (executives browse on phones)

### Example Inspirations
Stripe, Linear, Notion, HubSpot, Atlassian marketing pages

---

## REF: Event / Landing Page

### Standard Page Sections
1. **Hero with Countdown** — Event name, date, location, countdown timer, Register CTA
2. **Event Overview** — What is this event, who is it for, why attend
3. **Speakers / Performers** — Photo, name, title/role, short bio cards
4. **Schedule / Agenda** — Timeline of sessions, times, locations, speaker names
5. **Ticket Tiers** — Early bird, general, VIP with price and perks
6. **Venue / Location** — Map embed, venue name, address, travel tips
7. **Sponsors** — Logo grid of supporting sponsors by tier
8. **Past Event Highlights** — Photos/video from previous editions
9. **FAQ** — Common questions about registration, refunds, parking
10. **Footer CTA** — Final "Register Now" push before page end

### Content Patterns
- Speaker card: headshot, name, company, talk title
- Schedule row: time, session name, speaker, room/stage
- Ticket card: tier name, price, feature list, Register button

### UI Conventions
- Bold, energetic design — excitement and urgency
- Countdown timer is a strong conversion tool
- Mobile-optimized (event goers share links on phones)
- Social sharing buttons
- Clear single conversion goal: Register / Buy Ticket

### Example Inspirations
TED conference page, WWDC, music festival sites (Coachella, Glastonbury)

---

## REF: Other / Unknown

Use this section when the user's request does not clearly fit any of the predefined categories.

Examples that fall here:
- Educational / tutoring platform
- Healthcare / clinic / wellness
- News / magazine / blog
- Real estate / property listing
- Government / public service
- Gaming / esports
- Fitness / gym / sports club
- Finance / banking / investment
- Non-profit / charity / fundraising

### Step 1: Infer the closest domain
Even if it doesn't match a preset type, identify what domain it belongs to:
- What industry is this?
- Who are the users?
- What is the primary action users take on this site? (read, buy, book, sign up, browse, connect...)

### Step 2: Apply universal page section logic
Every website, regardless of type, needs these core sections. Adapt them to the domain:

1. **Hero / Above the Fold** — Headline that clearly states what the site is + primary CTA
2. **What We Offer** — Core value or service explanation (3-4 key points with icons)
3. **Featured Content / Showcase** — The main browsable content (articles, listings, profiles, classes, etc.)
4. **Social Proof** — Reviews, testimonials, statistics, press mentions, partner logos
5. **How It Works** — Step-by-step explanation if the service needs onboarding
6. **Call to Action Section** — Mid-page or bottom CTA to convert visitors
7. **Contact / Footer** — Links, social, legal, newsletter

### Step 3: Domain-specific must-haves

| Domain | Must-Have Elements |
|--------|--------------------|
| Education | Course cards, instructor profiles, syllabus preview, enrollment CTA |
| Healthcare | Services list, doctor profiles, appointment booking, trust certifications |
| News / Blog | Article cards with category tags, featured story hero, search bar |
| Real Estate | Property listing cards with photos/price/location, map view, filter/search |
| Fitness / Gym | Class schedule, trainer bios, membership tiers, before/after gallery |
| Gaming | Game showcase, leaderboard, community feed, download/play CTA |
| Finance | Product comparison table, calculator tool, security badges, FAQ |
| Non-profit | Mission statement, impact numbers, donation CTA, volunteer signup |

### Step 4: UI Defaults for Unknown Types
When style is not specified, use these safe defaults:
- **Color**: Clean white/light gray background with one strong brand accent color
- **Typography**: Clear, readable sans-serif — prioritize legibility over flair
- **Layout**: Card grid for browsable content, single column for text-heavy sections
- **Tone**: Professional and trustworthy unless user implies otherwise

### Example Inspirations
Coursera (education), Zocdoc (healthcare), The Verge (news/blog), Zillow (real estate), Peloton (fitness)
