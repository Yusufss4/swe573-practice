# SWE 573 Final Project Report

# Title Page

-   Yusuf Savaş
-   SWE 573 Final Project Report
-   December 19, 2025
-   Project Deployment URL: http://hive.yusufss.com/
-   Git Repo URL: https://github.com/Yusufss4/swe573-practice
-   Git Tag Version URL:
    https://github.com/Yusufss4/swe573-practice/releases/tag/v0.9
-   Video Demo URL: https://youtu.be/Y5k_Zd2y1k4
-   Deliverables URL: https://github.com/Yusufss4/swe573-practice/wiki

## Honor Code

Related to the submission of all the project deliverables for the Swe573
Fall 2025 semester project reported in this report, I
Yusuf Savaş declare that:
- I am a student in the Software Engineering MS program at Bogazici University and am registered for Swe573 course during the Fall 2025 semester.
- All the material that I am submitting related to my project (including but not limited to the project repository, the final project report, and supplementary documents) have been exclusively prepared by myself.
- I have prepared this material individually without the assistance of anyone else with the exception of permitted peer assistance, which I have explicitly disclosed in this report.

Yusuf Savaş

## Test Usernames

Test Username & Password for the project:

Regular Users (all use password: UserPass123!):

-   Username: alice
-   Username: bob
-   Username: carol
-   Username: david
-   Username: emma
-   Username: frank
-   Username: grace
-   Username: henry
-   Username: iris
-   Username: jack

Moderator: - Username: moderator - Password: ModeratorPass123!

## Work Declaration

I declare that the work submitted in this project report is solely my
own and has not been copied from any other source. I have cited all
sources used in this project, and have included proper attribution in
the report. AI Usage is declared in the project report as a seperate
section.

## Table of Contents

1. [Title Page](#title-page)
2. [Honor Code](#honor-code)
3. [Test Usernames](#test-usernames)
4. [Work Declaration](#work-declaration)
5. [Overview](#overview)
6. [Software Requirements Specification](#software-requirements-specification)
   - 6.1 [Introduction](#1-introduction)
   - 6.2 [Product Overview](#2-product-overview)
   - 6.3 [Requirements](#3-requirements)
     - 6.3.1 [Functional Requirements](#31-functional-requirements)
     - 6.3.2 [Non-Functional Requirements](#32-non-functional-requirements)
     - 6.3.3 [External Interfaces](#33-external-interfaces)
     - 6.3.4 [Compliance](#34-compliance)
     - 6.3.5 [Design and Implementation](#35-design-and-implementation)
   - 6.4 [Appendixes](#4-appendixes)
7. [Design Documents](#design-documents)
   - 7.1 [Mockup Screens](#mockup-screens)
   - 7.2 [Story Board](#story-board)
8. [The Hive - Requirements Implementation Status](#the-hive---requirements-implementation-status)
9. [Status of Deployment](#status-of-deployment)
10. [Installation Guide](#installation-guide)
    - 10.1 [Prerequisites](#prerequisites)
    - 10.2 [Local Development Installation](#local-development-installation)
    - 10.3 [Production Installation](#production-installation)
11. [System Requirements](#system-requirements)
12. [AI Usage Declaration](#ai-usage-declaration)
13. [User Manual](#user-manual)
14. [Use Case](#use-case)
15. [Test Plan](#test-plan)
16. [Project Plan](#project-plan)
17. [Credit & Licenses](#credit--licenses)
18. [Wiki Deliverables Link](#wiki-deliverables-link)

# Overview

The Hive is a time-banking community platform that enables service
exchange through a time-based currency system. Built as a full-stack web
application with a FastAPI backend and React TypeScript frontend, the
platform allows community members to offer and request services, using
time as the currency for exchanges. Users start with an initial balance
of 5 hours and can earn or spend time credits through completed
exchanges. A reciprocity limit of 10 hours helps maintain community
balance and prevent excessive debt.

The platform includes features to support community engagement and
trust-building. The core offers and needs system supports location-based
and remote options, capacity management, and time slot scheduling. The
handshake mechanism lets users propose help, accept or reject proposals,
and track exchanges from pending to completed status. A double-entry
bookkeeping system maintains transaction integrity, while a blind rating
system with multi-category feedback (Reliability, Kindness, Helpfulness)
enables fair evaluation of exchanges. Additional features include a
community forum for discussions and event announcements, real-time
WebSocket notifications, an interactive map with Leaflet for
location-based discovery, search and filtering capabilities, and a
moderation system with role-based access control. The semantic tag
system with hierarchical relationships and synonyms supports flexible
categorization and discovery, making The Hive a solution for building
and sustaining time-banking communities.

# Software Requirements Specification

About the SRS, - This template is based on IEEE 830.

## 1. Introduction

### 1.1 Purpose

The purpose of this Software Requirements Specification (SRS) document
is to define, in detail, the functional and non-functional requirements
of The Hive platform, a community-oriented, open-source web application
designed for the mutual exchange of services based on time rather than
money.

This document serves as a reference for:

-   Developers, who will design, implement, and maintain the platform.
-   Project stakeholders, who will ensure that the product aligns with
    its vision of inclusivity and cooperation.
-   Testers and quality engineers, who will verify that the delivered
    software meets the stated requirements.
-   Community moderators and administrators, who will oversee system
    behavior and enforce community standards.

The SRS establishes a common understanding of the platform's intended
capabilities, performance expectations, and design constraints,
providing a foundation for system design, implementation, and future
expansion.

### 1.2 Product Scope

The Hive is a virtual public space that enables individuals to exchange
services in a non-commercial, community-driven environment. Unlike
profit-oriented gig platforms, The Hive emphasizes cooperation,
reciprocity, and inclusivity.

Its main objectives are: - To provide a map-based interface for posting
and discovering service Offers and Needs. - To enable semantic tagging
for easy discovery and organization of activities. - To maintain a
TimeBank system where time, rather than money, serves as the unit of
value. - To support profile-based community trust, comments, and
transparent histories of contribution. - To allow users to connect,
communicate, and schedule services through a simple, privacy-aware
interface.

The software will be deployed as a web application with an open-source
architecture. The system will use a RESTful backend (Python Django REST
or Java Spring Boot) with a relational database (MySQL or PostgreSQL)
and will be containerized via Docker for deployment flexibility.

The primary goals of The Hive are: - To cultivate mutual support within
local and remote communities. - To ensure fairness through a balanced
exchange of time. - To maintain transparency and simplicity while
minimizing barriers to participation. - To promote sustainability by
supporting open contribution and community moderation.

### 1.3 Definitions, Acronyms and Abbreviations

  -----------------------------------------------------------------------------
  Term            Definition
  --------------- -------------------------------------------------------------
  **Offer**       A post created by a user describing a service they are
                  willing to provide (e.g., tutoring, cooking, repairs).

  **Need**        A post describing a service a user is requesting from the
                  community.

  **Handshake**   The process by which a requester explicitly accepts an offer
                  to finalize an exchange.

  **TimeBank**    A virtual currency system where 1 hour of service equals 1
                  TimeBank hour.

  **Semantic      A keyword or concept used to categorize and describe
  Tag**           offers/needs (e.g., *cooking*, *tutoring*).

  **Archive**     A record of completed or expired offers and needs. Completed
                  exchanges are visible on public profiles; expired items are
                  hidden by default and are only visible to the owner and
                  admins/moderators.

  **Moderator**   A user with privileges to review reports, manage comments,
                  and handle inappropriate content.

  **Admin**       A user with full system privileges, including moderator
                  management and tag curation.

  **Docker**      Containerization technology used for packaging and deploying
                  the application consistently across environments.

  **RESTful API** An application programming interface following the principles
                  of Representational State Transfer (REST).

  **Badge**       A non-rating recognition awarded automatically based on
                  objective participation/activity milestones (e.g., hours
                  contributed, exchanges completed).

  **Capacity**    The maximum number of participants that can be accepted for a
                  single Offer or Need.
  -----------------------------------------------------------------------------

### 1.4 References

-   IEEE 830-1998 -- IEEE Recommended Practice for Software Requirements
    Specifications.
-   Django REST Framework Documentation
    (https://www.django-rest-framework.org/).
-   Spring Boot Documentation (https://spring.io/projects/spring-boot).
-   PostgreSQL Official Documentation
    (https://www.postgresql.org/docs/).
-   WikiData Ontology for Semantic Tagging (https://www.wikidata.org/).
-   Docker Documentation (https://docs.docker.com/).

### 1.5 Overview

The remainder of this document is organized as follows: - Section 2 --
Product Overview: Describes the general factors that influence the
system and provides contextual information about The Hive. - Section 3
-- Requirements: Specifies detailed functional and non-functional
requirements, including system behavior, constraints, and interfaces. -
Section 4 -- Appendixes: Provides supporting material, such as a
glossary, diagrams, and supplementary explanations to aid understanding.

## 2. Product Overview

### 2.1 Product Perspective

The Hive is a new, self-contained, open-source web platform designed to
facilitate community-based service exchange through time-based
reciprocity. It does not replace or extend an existing commercial
system; rather, it introduces a non-monetary, trust-driven alternative
to traditional gig or marketplace applications.

The platform is composed of modular subsystems connected through a
RESTful backend API. At a high level, the architecture consists of:

**Frontend Web Application:** A responsive, map-based interface that
allows users to create, browse, and manage Offers and Needs, interact
through messaging, and track their TimeBank balance.

**Backend Service Layer:** Exposes RESTful endpoints for authentication,
user management, offers, needs, messaging, moderation, and TimeBank
transactions. Built using either Django REST Framework or Spring Boot.

**Database Layer:** A relational database (MySQL or PostgreSQL) storing
user profiles, posts, tags, transaction histories, and moderation data.

**Containerization and Deployment:** The application is deployed using
Docker, enabling consistent environment setup and portability across
different hosting platforms.

### 2.2 Product Functions

At a high level, The Hive provides the following major functional
capabilities:

**User Registration and Authentication**

-   Register new users and log in via secure credentials.
-   Manage profiles and TimeBank balance.

**Offers and Needs Management**

-   Create, edit, extend, or archive offers and needs.
-   Assign semantic tags and optional approximate location.
-   Indicate availability using the integrated calendar for offers.
-   Specify capacity (number of participants) for each Offer or Need.

**Handshake Mechanism**

-   Allow users to send offers of help with optional short messages.
-   Require explicit acceptance from the requester to finalize
    exchanges.

**Messaging System**

-   Enable text-based communication between participants of an active
    exchange.

**TimeBank Accounting**

-   Track contribution and consumption in hours.
-   Enforce the 10-hour reciprocity limit.

**Map-Based Discovery**

-   Visualize offers and needs geographically.
-   Filter by tags, distance, or online availability.
-   Default ordering for lists and map results is by distance from the
    user's set location.

**Profile and Comment System**

-   Publicly display participation history, tags, and archived
    exchanges.
-   Allow comment posting after exchange completion, moderated by
    content filters.
-   Display user badges earned via objective milestones.

**Badges and Recognition**

-   Award badges automatically when users meet objective milestones
    (e.g., hours contributed, exchanges completed).
-   Show badges on user profiles and next to display names on Offer/Need
    cards.
-   Recalculate badge eligibility on a scheduled job; dynamic badges may
    expire if criteria are no longer met.

**Admin and Moderation Tools**

-   Admins manage users, moderators, tags, and reported content.
-   Moderators handle content review, comment filtering, and report
    resolution.

**Reporting and Community Safety**

-   Users can report inappropriate content or behavior.
-   Moderators can review and remove reported items according to
    community guidelines.

**System Management**

-   Archive expired offers and completed exchanges.
-   Maintain transparency through publicly viewable activity histories.

**Community Forum**

-   Provide a space for community-wide discussions and event
    announcements.
-   Two tabs: Discussions and Events.

### 2.3 User Characteristics

  --------------------------------------------------------------------------------------------
  **User Class**  **Description**        **Technical        **Frequency   **Privileges**
                                         Expertise**        of Use**      
  --------------- ---------------------- ------------------ ------------- --------------------
  **Regular       General community      Basic computer and Moderate to   Can create
  User**          member who posts,      web navigation     high.         offers/needs,
                  offers, and            skills.                          message, comment,
                  participates in                                         and report content.
                  exchanges.                                              

  **Moderator**   Trusted user           Intermediate;      High.         Can remove
                  responsible for        familiar with                    inappropriate
                  maintaining community  moderation tools.                content, review
                  quality and handling                                    flagged posts, and
                  reports.                                                manage comments.

  **Admin**       Platform operator      Advanced;          Continuous.   Full control: manage
                  overseeing system      technical                        users, moderators,
                  health, data           knowledge of                     tags, and reports.
                  consistency, and       system operation                 
                  community governance.  and data                         
                                         management.                      
  --------------------------------------------------------------------------------------------

### 2.4 Constraints

**Design and Implementation Constraints**

-   The system must be web-based during the initial release.
-   The backend must provide RESTful APIs.
-   The application must be Dockerized for deployment.
-   Database must be MySQL or PostgreSQL.
-   Backend language must be Python (Django REST) or Java (Spring Boot).
-   No external authentication (OAuth) or calendar synchronization.
-   No accessibility or dark-mode support required in the initial
    version.

**Functional Constraints**

-   Offers are valid for 7 days by default; users may extend or renew
    but not shorten.
-   Each user starts with 5 TimeBank hours.
-   When a user reaches a 10-hour surplus, they must create a Need to
    restore balance.
-   Location data must be approximate only; no exact addresses are
    stored.
-   Communication is text-only; no video or audio integration.
-   Each exchange must involve a handshake for confirmation.
-   Offers and Needs may specify a capacity \> 1 (default 1). The system
    shall prevent accepting more participants than the declared
    capacity.
-   Expired Offers/Needs shall not be displayed on public profile pages.
    Owners may access their own expired items in a private "Archived"
    view or via filters.

**Community and Governance Constraints**

-   No voting or rating system is implemented.
-   Comments are moderated by an automated filter.
-   Community guidelines define acceptable behavior.
-   Reports of inappropriate content must be reviewable by moderators.

### 2.5 Assumptions and Dependencies

**Assumptions**

-   Users act in good faith and understand the community guidelines.
-   Internet connectivity is stable enough for interactive map and
    messaging operations.
-   The user community remains small in the initial phase (hundreds of
    active users).
-   Users voluntarily provide approximate location or mark their service
    as remote.
-   The majority of services are non-monetary and informal.

**Dependencies**

The system depends on: - A functional mapping API (e.g., OpenStreetMap
or Google Maps API) for displaying offers and needs. - A stable Docker
runtime environment for deployment. - Relational database availability
for persistent data storage. - The system assumes availability of
standard web browsers that support modern HTML5 features.

## 3. Requirements

### 3.1 Functional Requirements

The following requirements define the functional behavior of The Hive.
Each requirement is labeled FR--X for traceability and verification
purposes.

**FR--1: User Registration and Authentication**

-   FR--1.1 The system shall allow users to register with a unique
    username, email, and password.
-   FR--1.2 The system shall validate email format and password
    complexity upon registration.
-   FR--1.3 The system shall provide login and logout functionality.
-   FR--1.4 The system shall encrypt all stored passwords using secure
    hashing.
-   FR--1.5 The system shall provide session-based authentication for
    authorized access.

**FR--2: Profile Management**

-   FR--2.1 Each user shall have a public profile displaying their
    semantic tags, total hours given/received, badges, archived
    exchanges, and comments.
-   FR--2.2 The system shall display a user's current TimeBank balance
    on their profile.
-   FR--2.3 The profile shall show an archive of completed exchanges.
    Expired Offers/Needs shall be hidden by default on public profiles;
    the owner may optionally view expired items via a private filter.
-   FR--2.4 Users shall be able to edit personal details such as display
    name and description.
-   FR--2.5 The system shall automatically moderate user descriptions
    using keyword filters.

**FR--3: Offer and Need Management**

-   FR--3.1 The system shall allow users to create Offers and Needs
    containing:
    -   Title
    -   Description
    -   Tags
    -   Approximate location (if it is not remote, it is required)
    -   Duration (default 7 days)
    -   Remote/in-person indicator
    -   Capacity (default 1)
-   FR--3.2 Users shall be able to renew or extend offers but not
    shorten their expiration date.
-   FR--3.3 Offers and needs shall automatically archive after
    expiration.
-   FR--3.4 Users shall be able to mark their offers as remote.
-   FR--3.5 Users shall assign one or more semantic tags when posting.
-   FR--3.6 The system shall track the number of accepted participants
    for each Offer/Need and shall not allow accepting more participants
    than the declared capacity.
-   FR--3.7 Capacity may be increased while a post is active; it shall
    not be decreased below the current number of accepted participants.

**FR--4: Calendar and Availability**

-   FR--4.1 The system shall allow users creating an Offer to define
    available time slots using an internal calendar.
-   FR--4.2 A requester viewing the offer shall be able to select one of
    the available hours for scheduling.
-   FR--4.3 The calendar feature shall not synchronize with any external
    calendar systems.

**FR--5: Handshake Mechanism**

-   FR--5.1 When a user offers help on a posted need, the system shall
    prompt for an optional short message.
-   FR--5.2 The offer shall be marked as pending until the requester
    explicitly accepts or rejects it.
-   FR--5.3 Once accepted, the exchange shall be marked as confirmed and
    become active.
-   FR--5.4 The system shall record the date and duration of the
    confirmed exchange in both users' histories.
-   FR--5.5 A Need or Offer may accept multiple participants up to its
    capacity. Each acceptance shall increment the accepted participant
    count.
-   FR--5.6 When accepted participants reach capacity, the post shall be
    marked Full and no additional requests may be accepted.

**FR--6: Messaging System**

-   FR--6.1 The system shall allow text-based communication between
    participants in an active exchange.
-   FR--6.2 Messages shall be private and visible only to participants.
-   FR--6.3 Messaging shall be disabled after an exchange is marked
    complete.

**FR--7: TimeBank System**

-   FR--7.1 Each user shall start with an initial balance of 5 hours.
-   FR--7.2 The system shall update the TimeBank balance automatically
    when an exchange is completed:
    -   The provider gains hours.
    -   The requester loses hours.
-   FR--7.3 Users shall not exceed a balance of +10 hours without
    opening a Need.
-   FR--7.5 All TimeBank transactions shall be logged for auditability.
-   FR--7.6 For exchanges with multiple participants, the system shall
    record a separate transaction per participant reflecting the actual
    hours contributed and received.
-   FR--7.7 Anti-hoarding rule (multi-participant): A provider
    facilitating a session with multiple requesters shall earn at most
    the actual session duration once (e.g., a 1-hour session with 3
    requesters credits the provider 1 hour total, not 3). Each requester
    is debited individually (3 requesters each pay 1 hour -\> total
    debited 3 hours).

**FR--8: Tagging and Search**

-   FR--8.1 The system shall use semantic tags to describe Offers and
    Needs.
-   FR--8.2 Users shall be able to search and filter content by tags.
-   FR--8.3 Users shall be able to create new tags freely.
-   FR--8.4 Tags shall follow a simple hierarchy inspired by WikiData's
    tagging model.
-   FR--8.5 Default ordering for lists and map results shall be by
    distance from the user's set location.

**FR--9: Map-Based Visualization**

-   FR--9.1 The system shall display Offers and Needs on an interactive
    map.
-   FR--9.2 Locations shall always be approximate, never exact
    addresses.
-   FR--9.3 The map shall visually differentiate between Offers and
    Needs.
-   FR--9.4 The map shall allow filtering by distance, tag, and service
    type.

**FR--10: Comment and Feedback System**

-   FR--10.1 After completing an exchange, both participants may leave a
    comment on each other's profile.
-   FR--10.2 All comments shall pass through automated text moderation
    filters.
-   FR--10.3 Comments shall be publicly visible on profiles.

**FR--11: Reporting and Moderation**

-   FR--11.1 Users shall be able to report inappropriate content or
    behavior.
-   FR--11.2 Moderators shall review and take action on reports (e.g.,
    remove content or warn users).
-   FR--11.3 Admins shall have the ability to manage moderators and
    system-wide settings.
-   FR--11.4 Reports and their resolutions shall be logged in the system
    for transparency.

**FR--12: Archiving and Transparency**

-   FR--12.1 The system shall automatically archive expired or completed
    Offers and Needs.
-   FR--12.2 Completed archived content shall be visible under each
    user's public profile. Expired items shall be hidden by default on
    public profiles; owners may access expired items in a private
    archived view.
-   FR--12.3 Users shall be able to view their past exchanges, including
    dates and durations.

**FR--14: Active Items Management**

-   FR--14.1 The system shall provide a dedicated "Active Items" page
    for authenticated users to manage ongoing participation.
-   FR--14.2 The Active Items page shall present separate sections/tabs:
    -   My Active Offers
    -   My Active Needs
    -   Applications I Submitted (pending/accepted)
    -   Accepted Participation (exchanges where I'm an accepted
        participant)
-   FR--14.3 Each item on this page shall show status (Pending,
    Confirmed/Active, Full), capacity/accepted counts, and quick actions
    (view, message, cancel/withdraw where applicable).
-   FR--14.4 The Active Items page shall not display expired or
    completed items; those are available in Archived views.

**FR--15: Community Forum**

-   FR--15.1 The system shall provide a Community Forum accessible to
    authenticated users with two tabs: Discussions and Events.
-   FR--15.2 Discussions tab shall allow users to create discussion
    topics with title and body, post comments, and search by keywords
    and tags.
-   FR--15.3 Events tab shall allow users to create event posts with
    title, description, date/time, optional location (approximate or
    remote), and tags.
-   FR--15.4 Forum posts and comments shall be moderated by the same
    reporting and moderation tools defined in FR--11.
-   FR--15.5 Event posts may optionally link to an Offer or Need; such
    links shall be displayed on both the event and the linked item
    pages.
-   FR--15.6 Forum lists default ordering shall be by recency; users may
    filter by tag.

**FR--13: Badges**

-   FR--13.1 The system shall award badges automatically based on
    objective criteria derived from system data; no manual endorsements
    or ratings are required.
-   FR--13.2 The system shall display earned badges on the user's
    profile and next to the user's display name on Offer/Need cards.
-   FR--13.3 Badge eligibility shall be recalculated on a scheduled
    basis (e.g., daily). Some badges may be dynamic and expire if
    criteria are no longer met; milestone badges remain once earned.
-   FR--13.4 The initial badge set shall include (at minimum):
    -   Helper I/II/III: total hours contributed \>= 5 / 25 / 100.
    -   Exchange Starter I/II: completed exchanges \>= 5 / 20.
    -   Tag Specialist: \>= 3 completed exchanges under the same primary
        tag.
    -   All‑Rounder: completed exchanges in \>= 5 distinct tags.
    -   Consistent Contributor: \>= 5 completed exchanges within the
        last 60 days (dynamic).
    -   Veteran Bee: account age \>= 1 year and completed exchanges \>=
        20.
-   FR--13.5 The system shall provide an admin-visible catalog of badge
    definitions with codes, names, descriptions, and criteria
    references.
-   FR--13.6 Badges shall be informational and non-rating; they shall
    not affect search ranking or access rights.

### 3.2 Non-Functional Requirements

#### 3.2.1 Performance

-   NFR--1 The system shall support at least 500 concurrent users with
    no more than 3-second response time for page loads.
-   NFR--2 Map data and service listings shall load asynchronously for
    responsiveness.
-   NFR--3 Backend API shall handle at least 50 requests per second
    under normal conditions..

#### 3.2.2 Security

-   NFR--4 All user authentication shall use encrypted HTTPS
    connections.
-   NFR--5 Passwords shall be stored as salted hashes.
-   NFR--6 User messages and profiles shall be accessible only to
    authenticated users.
-   NFR--7 Location data shall be generalized to prevent revealing exact
    addresses.
-   NFR--8 Admin and moderator actions shall be logged for audit
    tracking.

#### 3.2.3 Reliability

-   NFR--9 The system shall be available 95% of the time in normal
    operation.
-   NFR--10 Data integrity shall be maintained through daily database
    backups.
-   NFR--11 The application shall handle failures gracefully, displaying
    appropriate fallback messages.

#### 3.2.4 Availability

-   NFR--12 In case of temporary downtime, users shall be notified
    through a maintenance page.
-   NFR--13 Archived data shall remain accessible even during limited
    system maintenance.

### 3.3 External Interfaces

#### 3.3.1 User interfaces

The platform shall include:

-   A home map view showing all Offers and Needs.
-   A sidebar list view displaying nearby posts as cards.
-   Offer/Need forms for creating posts with title, description, tags,
    and location.
-   Profile pages with public activity summaries and comments.
-   Badge display on profiles and next to display names where
    appropriate.
-   An "Active Items" dashboard page with sections for My Active Offers,
    My Active Needs, Applications I Submitted, and Accepted
    Participation.
-   A Community Forum with two tabs: Discussions and Events.
-   Admin dashboard for system overview, reports, and tag management.
-   Moderator dashboard for reviewing reports and managing content.
-   All interfaces shall follow a clean, accessible layout with
    consistent navigation.
-   No accessibility-specific features (screen reader, dark mode) are
    required in the initial version.

#### 3.3.2 Hardware interfaces

-   No dedicated hardware interfaces are required.
-   The system will operate on any standard web-enabled device (PC,
    tablet, or smartphone).

#### 3.3.3 Software interfaces

-   Frontend -\> Backend: RESTful API (JSON over HTTPS).
-   Backend -\> Database: SQL-based interaction (MySQL or PostgreSQL).
-   Optional External API: Mapping API for geolocation visualization.
-   Containerization: Docker for packaging and deployment.

### 3.4 Compliance

-   The software shall comply with open-source licensing terms defined
    for the project repository.
-   All logs related to moderation and transactions shall maintain basic
    audit trails.
-   Data formats (JSON for APIs, SQL for storage) shall adhere to
    industry conventions.
-   The project shall follow basic community data protection principles
    (no unnecessary personal data).

### 3.5 Design and Implementation

### 3.5.1 Database Requirements

The relational schema shall include:

-   Users: id, name, email, password hash, balance, role.
-   Offers/Needs: id, type, title, description, location (approx.),
    creator_id, tags, start_date, end_date, status, capacity,
    accepted_count.
-   TimeBankTransactions: id, sender_id, receiver_id, amount, timestamp,
    type (exchange).
-   Comments: id, from_user, to_user, content, timestamp.
-   Reports: id, reported_item_id, reason, reporter_id,
    moderator_action.
-   Tags: id, name, related_tags.
-   Participants: id, post_id, user_id, role (provider/requester),
    status (pending/accepted/declined/completed), hours_contributed.
-   UserBadges: id, user_id, badge_code, awarded_at.
-   ForumTopics: id, author_id, title, body, tags, created_at,
    updated_at, status (active/locked/removed), type (discussion/event),
    event_start_at, event_end_at, event_location.
-   ForumComments: id, topic_id, author_id, body, created_at,
    updated_at, status (active/removed).

### 3.5.2 Design Constraints

-   Backend must use either Python (Django REST Framework) or Java
    (Spring Boot).
-   Database must be MySQL or PostgreSQL.
-   Deployment must be Dockerized.
-   Frontend must be web-based using HTML5, CSS, and JavaScript.
-   APIs must follow REST design principles with JSON responses.

## 4. Appendixes

### 4.1 Glossary

  ---------------------------------------------------------------------------------
  **Term**           **Definition**
  ------------------ --------------------------------------------------------------
  **Admin**          A privileged user responsible for managing moderators,
                     reviewing reports, handling user disputes, and maintaining tag
                     integrity. Has full control over system settings.

  **Archive**        A historical record of completed or expired Offers and Needs.
                     Completed items are visible on public profiles; expired items
                     are hidden by default and visible to owners in a private view.

  **Calendar         A scheduling component that allows users posting an Offer to
  (Availability)**   specify available time slots for others to book.

  **Comment**        Feedback or short message left by a participant after
                     completing an exchange. Comments are public and automatically
                     filtered for inappropriate content.

  **Community        A set of behavioral rules designed to promote respect, trust,
  Guidelines**       and constructive interaction within *The Hive*. These
                     guidelines replace any formal rating or reputation system.

  **Docker**         A containerization platform used for consistent deployment and
                     environment replication.

  **Handshake**      The mutual agreement process between a requester and an
                     offerer to finalize a service exchange. The requester must
                     explicitly accept the offer for it to be confirmed.

  **Moderator**      A user role responsible for maintaining community quality by
                     managing reports, filtering content, and enforcing guidelines.

  **Need**           A service request posted by a user (e.g., "Help assembling
                     furniture" or "Assistance with a computer setup").

  **Offer**          A service proposal posted by a user (e.g., "Tutoring in math"
                     or "Cooking a traditional meal"). Offers can include optional
                     availability hours and can be remote or location-based.

  **Profile**        A public user page displaying summary information, active and
                     archived Offers/Needs, comments, and TimeBank balance.

  **Remote Service** An Offer or Need that does not require physical proximity,
                     such as online tutoring or digital collaboration.

  **Report**         A user-submitted flag indicating inappropriate or unsafe
                     behavior or content.

  **Semantic Tag**   A descriptive keyword or concept associated with an Offer or
                     Need, such as *cooking*, *tutoring*, or *companionship*. Tags
                     can be created by users and are inspired by WikiData's
                     semantic model.

  **TimeBank**       A virtual currency mechanism where one hour of service equals
                     one TimeBank hour. It promotes fairness and reciprocity within
                     the community.

  **User Role**      Defines permissions and responsibilities: *Regular User*,
                     *Moderator*, or *Admin*.

  **Web              The browser-based interface of *The Hive*, accessible via
  Application**      desktop or mobile devices, used for all interactions,
                     including map viewing, messaging, and management.

  **Badge**          A non-rating visual marker automatically awarded when a user
                     meets objective participation criteria (e.g., hours,
                     exchanges).

  **Capacity**       The maximum number of participants that can be accepted for a
                     single Offer or Need.

  **Community        A space in the application with two tabs: Discussions for
  Forum**            ongoing community topics and Events for announcements with
                     date/time and optional location.

  **Discussion**     A forum topic consisting of a title and body where users can
                     comment and converse asynchronously.

  **Event**          A forum topic announcing a scheduled happening with date/time
                     and optional location, optionally linked to an Offer or Need.
  ---------------------------------------------------------------------------------

# Design Documents

## Mockup Screens

### Figma

[The Hive Mockup Screens
Figma](https://www.figma.com/make/OlezttiIMSgYebtAUI22DN/The-Hive-Mockup-Design?fullscreen=1)

------------------------------------------------------------------------

### Screens

#### Interactive Map View

Users explore nearby offers and needs on a map, filter by category, and
see details of each request in the sidebar.\
![Interactive Map
View](https://github.com/user-attachments/assets/57ebab06-6c25-41ce-b909-3ff75754b549)

------------------------------------------------------------------------

#### Offer Detail View

Shows full information about a specific offer, including description,
tags, time slots, and the option to request a service.\
![Offer Detail
View](https://github.com/user-attachments/assets/76526723-e3af-4f54-bbce-9d9ed85d6091)

------------------------------------------------------------------------

#### Request Service Modal

Allows users to confirm participation by selecting a time slot and
sending a short message to the offer owner.\
![Request Service
Modal](https://github.com/user-attachments/assets/3225b0ce-2c6c-4938-b5a0-accbfdf417d5)

------------------------------------------------------------------------

#### User Profile Page

Displays a member's bio, badges, TimeBank balance, and feedback from
completed exchanges for transparency and trust.\
![User Profile
Page](https://github.com/user-attachments/assets/bfec0e07-ca0f-4a09-b00f-6d1307325a6b)

------------------------------------------------------------------------

#### Active Items -- Applicants

Lets requesters review and manage applications from helpers, with the
ability to accept or decline each one.\
![Active Items --
Applicants](https://github.com/user-attachments/assets/aa90911d-33c7-4dea-ac74-bebd930a004b)

------------------------------------------------------------------------

#### Active Items -- Applications

Allows helpers to track the status of their submitted applications and
communicate or withdraw when needed.\
![Active Items --
Applications](https://github.com/user-attachments/assets/4f533364-70e7-4583-94dc-83a3ab223a72)

------------------------------------------------------------------------

#### Messaging Page

Provides a simple chat interface for users to discuss details and
coordinate after a connection is made.\
![Messaging
Page](https://github.com/user-attachments/assets/b1c69d45-bcc4-41b8-b190-2a9b076f52d0)

------------------------------------------------------------------------

## Story Board

![TheHiveStoryBoard](https://github.com/user-attachments/assets/7e97e819-f330-4326-9a17-b802f16d158d)

# The Hive - Requirements Implementation Status

This document tracks the implementation status of all requirements from
the Software Requirements Specification (SRS).

**Legend:** - \[Complete\] **Complete** - Fully implemented and tested -
\[Partial\] **Partial** - Partially implemented or needs enhancement -
\[Not Complete\] **Not Complete** - Not yet implemented

------------------------------------------------------------------------

## 3.1 Functional Requirements

### FR-1: User Registration and Authentication

  -------------------------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- -----------------------------------
  FR-1.1   Register with unique         \[Complete\]      `app/api/auth.py`,
           username, email, and                           `frontend/src/pages/Register.tsx`
           password                                       

  FR-1.2   Validate email format and    \[Complete\]      Email validation via Pydantic
           password complexity                            EmailStr, password min 8 chars with
                                                          complexity rules

  FR-1.3   Login and logout             \[Complete\]      JWT-based authentication with
           functionality                                  login/logout endpoints

  FR-1.4   Encrypt stored passwords     \[Complete\]      bcrypt with salt in
           using secure hashing                           `app/core/security.py`

  FR-1.5   Session-based authentication \[Complete\]      JWT tokens with 7-day expiration
           for authorized access                          
  -------------------------------------------------------------------------------------------

### FR-2: Profile Management

  ----------------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- --------------------------
  FR-2.1   Public profile with tags,    \[Complete\]      `ProfilePage.tsx` shows
           hours, badges, exchanges,                      all profile elements
           comments                                       

  FR-2.2   Display TimeBank balance on  \[Complete\]      Balance shown in stats
           profile                                        section

  FR-2.3   Archive of completed         \[Complete\]      Separate tabs for
           exchanges; expired items                       active/completed, expired
           hidden by default                              filtering

  FR-2.4   Edit personal details        \[Complete\]      Edit dialog with name,
           (display name, description)                    bio, avatar, social links

  FR-2.5   Auto-moderate user           \[Complete\]      `app/core/moderation.py`
           descriptions using keyword                     with profanity/spam checks
           filters                                        
  ----------------------------------------------------------------------------------

### FR-3: Offer and Need Management

  ------------------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- ----------------------------
  FR-3.1   Create Offers/Needs with     \[Complete\]      Full implementation in
           title, description, tags,                      `app/api/offers.py`,
           location, duration, remote                     `app/api/needs.py`
           indicator, capacity                            

  FR-3.2   Renew/extend offers but not  \[Complete\]      `OfferExtend` schema
           shorten expiration                             validates extension only

  FR-3.3   Auto-archive after           \[Complete\]      `archive_expired_items()` in
           expiration                                     `app/core/offers_needs.py`

  FR-3.4   Mark offers as remote        \[Complete\]      `is_remote` field with
                                                          location validation

  FR-3.5   Assign one or more semantic  \[Complete\]      Tag association tables and
           tags when posting                              frontend tag picker

  FR-3.6   Track accepted participants  \[Complete\]      `accepted_count` field,
           vs capacity                                    capacity enforcement

  FR-3.7   Capacity can increase but    \[Complete\]      Validation in update
           not decrease below accepted                    endpoints
           count                                          
  ------------------------------------------------------------------------------------

### FR-4: Calendar and Availability

  -------------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- -----------------------
  FR-4.1   Define available time slots  \[Complete\]      `TimeSlotPicker.tsx`,
           using internal calendar                        `available_slots` JSON
                                                          field

  FR-4.2   Requester can select         \[Partial\]       Time slot display
           available hours for                            works; selection stored
           scheduling                                     in participant record

  FR-4.3   No external calendar         \[Complete\]      Internal only, no
           synchronization                                external API
                                                          integration
  -------------------------------------------------------------------------------

### FR-5: Handshake Mechanism

  -------------------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- -----------------------------
  FR-5.1   Propose help with optional   \[Complete\]      `app/api/handshake.py` with
           short message                                  message field

  FR-5.2   Proposal marked pending      \[Complete\]      `ParticipantStatus.PENDING`
           until accepted/rejected                        -\> `ACCEPTED/DECLINED`

  FR-5.3   Once accepted, exchange      \[Complete\]      Status transitions with
           marked confirmed/active                        capacity updates

  FR-5.4   Record date and duration in  \[Complete\]      Ledger entries and
           both users' histories                          participant records

  FR-5.5   Accept multiple participants \[Complete\]      `accepted_count` incremented
           up to capacity                                 on accept

  FR-5.6   Mark post as Full when       \[Complete\]      Status changes to `FULL`
           capacity reached                               automatically
  -------------------------------------------------------------------------------------

### FR-6: Messaging System

  -----------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- ---------------
  FR-6.1   Text-based communication     \[Not Complete\]  Message types
           between participants                           defined but no
                                                          messaging API

  FR-6.2   Messages private and visible \[Not Complete\]  Not implemented
           only to participants                           

  FR-6.3   Messaging disabled after     \[Not Complete\]  Not implemented
           exchange complete                              
  -----------------------------------------------------------------------

### FR-7: TimeBank System

  -------------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- -----------------------
  FR-7.1   Initial balance of 5 hours   \[Complete\]      Default in User model
                                                          and registration

  FR-7.2   Auto-update balance on       \[Complete\]      `complete_exchange()`
           exchange completion                            in `app/core/ledger.py`

  FR-7.3   Cannot exceed +10 hours      \[Partial\]       Reciprocity limit
           without opening a Need                         implemented but not
                                                          Need requirement

  FR-7.5   All transactions logged for  \[Complete\]      `LedgerEntry` model
           auditability                                   with full audit trail

  FR-7.6   Separate transaction per     \[Complete\]      Individual ledger
           participant                                    entries per participant

  FR-7.7   Anti-hoarding rule (provider \[Not Complete\]  Provider earns per
           earns once for                                 exchange, not
           multi-requester session)                       session-based
  -------------------------------------------------------------------------------

### FR-8: Tagging and Search

  -------------------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- -----------------------------
  FR-8.1   Semantic tags to describe    \[Complete\]      Full tag system with
           Offers and Needs                               WikiData-style features

  FR-8.2   Search and filter by tags    \[Complete\]      `app/api/search.py` with tag
                                                          filtering

  FR-8.3   Users can create new tags    \[Complete\]      Auto-creation on use
           freely                                         

  FR-8.4   Tags follow                  \[Complete\]      Parent-child, synonyms,
           WikiData-inspired hierarchy                    properties in
                                                          `app/core/semantic_tags.py`

  FR-8.5   Default ordering by distance \[Complete\]      Distance sorting in map feed
           from user location                             and search
  -------------------------------------------------------------------------------------

### FR-9: Map-Based Visualization

  --------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- ------------------
  FR-9.1   Display Offers and Needs on  \[Complete\]      Leaflet map in
           interactive map                                `MapView.tsx`

  FR-9.2   Locations always             \[Complete\]      Coordinates
           approximate, never exact                       rounded to \~1km
                                                          in
                                                          `app/api/map.py`

  FR-9.3   Visually differentiate       \[Complete\]      Different colored
           Offers and Needs                               markers
                                                          (green/blue)

  FR-9.4   Filter by distance, tag, and \[Complete\]      Full filter drawer
           service type                                   with all options
  --------------------------------------------------------------------------

### FR-10: Comment and Feedback System

  -------------------------------------------------------------------------------
  ID        Requirement                  Status            Notes
  --------- ---------------------------- ----------------- ----------------------
  FR-10.1   Both participants can leave  \[Complete\]      Rating system with
            comment after exchange                         public comments

  FR-10.2   Comments pass through        \[Complete\]      `moderate_content()`
            automated text moderation                      called before saving

  FR-10.3   Comments publicly visible on \[Complete\]      Ratings tab on profile
            profiles                                       page
  -------------------------------------------------------------------------------

### FR-11: Reporting and Moderation

  ------------------------------------------------------------------------------------
  ID        Requirement                  Status            Notes
  --------- ---------------------------- ----------------- ---------------------------
  FR-11.1   Report inappropriate content \[Complete\]      `app/api/reports.py` with
            or behavior                                    multiple report types

  FR-11.2   Moderators review and take   \[Complete\]      `ModeratorDashboard.tsx`,
            action                                         status updates, actions

  FR-11.3   Admins manage moderators and \[Complete\]      Admin role with moderator
            system settings                                management

  FR-11.4   Reports and resolutions      \[Complete\]      Timestamps: created_at,
            logged for transparency                        reviewed_at, resolved_at
  ------------------------------------------------------------------------------------

### FR-12: Archiving and Transparency

  ----------------------------------------------------------------------------
  ID        Requirement                  Status            Notes
  --------- ---------------------------- ----------------- -------------------
  FR-12.1   Auto-archive                 \[Complete\]      Status transitions
            expired/completed Offers and                   to
            Needs                                          EXPIRED/COMPLETED

  FR-12.2   Completed archived content   \[Complete\]      Completed exchanges
            visible on public profile                      tab on profile

  FR-12.3   View past exchanges with     \[Complete\]      Exchange history
            dates and durations                            with full details
  ----------------------------------------------------------------------------

### FR-13: Badges

  ------------------------------------------------------------------------------
  ID        Requirement                  Status            Notes
  --------- ---------------------------- ----------------- ---------------------
  FR-13.1   Award badges automatically   \[Partial\]       Frontend-calculated
            based on objective criteria                    badges in
                                                           `ProfilePage.tsx`

  FR-13.2   Display badges on profile    \[Partial\]       Profile display
            and Offer/Need cards                           works; card display
                                                           partial

  FR-13.3   Badge eligibility            \[Partial\]       Real-time
            recalculated periodically;                     calculation, no
            some dynamic                                   scheduled
                                                           recalculation

  FR-13.4   Initial badge set (Helper    \[Partial\]       Similar badges exist
            I/II/III, Exchange Starter,                    but not exact spec
            etc.)                                          badges

  FR-13.5   Admin-visible badge catalog  \[Not Complete\]  No admin badge
                                                           management UI

  FR-13.6   Badges informational only,   \[Complete\]      Badges don't affect
            no ranking effects                             search/access
  ------------------------------------------------------------------------------

### FR-14: Active Items Management

  ----------------------------------------------------------------------------------
  ID        Requirement                  Status            Notes
  --------- ---------------------------- ----------------- -------------------------
  FR-14.1   Dedicated "Active Items"     \[Complete\]      `ActiveItems.tsx` with
            page for authenticated users                   full dashboard

  FR-14.2   Separate sections: My        \[Complete\]      Two-tab layout with all
            Offers, My Needs,                              sections
            Applications, Participations                   

  FR-14.3   Show status, capacity, quick \[Complete\]      Status badges, counts,
            actions                                        accept/decline/complete
                                                           actions

  FR-14.4   No expired/completed items   \[Complete\]      Filtered to active only
            (available in Archives)                        
  ----------------------------------------------------------------------------------

### FR-15: Community Forum

  -----------------------------------------------------------------------------
  ID        Requirement                  Status            Notes
  --------- ---------------------------- ----------------- --------------------
  FR-15.1   Community Forum with         \[Complete\]      `Forum.tsx` with
            Discussions and Events tabs                    tabbed layout

  FR-15.2   Discussions: create topics,  \[Complete\]      Full CRUD for
            post comments, search                          discussions

  FR-15.3   Events: title, description,  \[Complete\]      Event-specific
            date/time, location, tags                      fields in model

  FR-15.4   Forum posts moderated by     \[Complete\]      Reports can target
            same tools as FR-11                            forum content

  FR-15.5   Events can link to           \[Complete\]      `linked_offer_id`,
            Offer/Need (bidirectional)                     `linked_need_id`
                                                           fields

  FR-15.6   Default ordering by recency; \[Complete\]      Created_at ordering,
            filter by tag                                  tag filtering
  -----------------------------------------------------------------------------

------------------------------------------------------------------------

## 3.2 Non-Functional Requirements

### 3.2.1 Performance

  -----------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- ---------------
  NFR-1    Support 500 concurrent       \[Partial\]       Not load
           users, \<3s page load                          tested; basic
                                                          optimization
                                                          done

  NFR-2    Map data loads               \[Complete\]      React Query
           asynchronously                                 async loading

  NFR-3    Backend handles 50 req/sec   \[Partial\]       Not benchmarked
  -----------------------------------------------------------------------

### 3.2.2 Security

  --------------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- ------------------------
  NFR-4    HTTPS encrypted connections  \[Complete\]      nginx.prod.conf with SSL
                                                          config

  NFR-5    Passwords stored as salted   \[Complete\]      bcrypt in
           hashes                                         `app/core/security.py`

  NFR-6    User data accessible only to \[Complete\]      JWT auth required for
           authenticated users                            protected endpoints

  NFR-7    Location data generalized    \[Complete\]      Coordinates rounded to
           (no exact addresses)                           \~1km

  NFR-8    Admin/moderator actions      \[Complete\]      Timestamps and audit
           logged                                         fields on reports
  --------------------------------------------------------------------------------

### 3.2.3 Reliability

  -----------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- ---------------
  NFR-9    95% availability             \[Partial\]       Docker
                                                          deployment; no
                                                          HA setup

  NFR-10   Daily database backups       \[Not Complete\]  No backup
                                                          automation
                                                          configured

  NFR-11   Graceful error handling with \[Complete\]      Error
           fallback messages                              boundaries and
                                                          API error
                                                          handling
  -----------------------------------------------------------------------

### 3.2.4 Availability

  ------------------------------------------------------------------------
  ID       Requirement                  Status            Notes
  -------- ---------------------------- ----------------- ----------------
  NFR-12   Maintenance page during      \[Not Complete\]  No maintenance
           downtime                                       mode

  NFR-13   Archived data accessible     \[Partial\]       No specific
           during limited maintenance                     maintenance mode
                                                          implementation
  ------------------------------------------------------------------------

------------------------------------------------------------------------

## 3.3 External Interfaces

### 3.3.1 User Interfaces

  -----------------------------------------------------------------------------
  Feature                    Status                  Notes
  -------------------------- ----------------------- --------------------------
  Home map view with         \[Complete\]            `MapView.tsx`
  Offers/Needs                                       

  Sidebar list view with     \[Complete\]            Integrated in MapView
  cards                                              

  Offer/Need creation forms  \[Complete\]            `CreateOffer.tsx`,
                                                     `CreateNeed.tsx`

  Profile pages with         \[Complete\]            `ProfilePage.tsx`
  activity summaries                                 

  Badge display on profiles  \[Complete\]            Badge section in profile

  Active Items dashboard     \[Complete\]            `ActiveItems.tsx`

  Community Forum            \[Complete\]            `Forum.tsx`,
  (Discussions & Events)                             `ForumTopicDetail.tsx`

  Admin dashboard            \[Complete\]            `AdminDashboard.tsx`

  Moderator dashboard        \[Complete\]            `ModeratorDashboard.tsx`

  Clean, accessible layout   \[Complete\]            Material-UI components
  -----------------------------------------------------------------------------

### 3.3.3 Software Interfaces

  --------------------------------------------------------------------------------
  Interface                      Status                Notes
  ------------------------------ --------------------- ---------------------------
  Frontend -\> Backend: RESTful  \[Complete\]          FastAPI with OpenAPI docs
  API (JSON/HTTPS)                                     

  Backend -\> Database: SQL      \[Complete\]          SQLModel/SQLAlchemy
  (PostgreSQL)                                         

  Mapping API for geolocation    \[Complete\]          Leaflet with OpenStreetMap
                                                       tiles

  Docker containerization        \[Complete\]          `docker-compose.yml`,
                                                       `docker-compose.prod.yml`
  --------------------------------------------------------------------------------

------------------------------------------------------------------------

## 3.5 Design and Implementation

### 3.5.1 Database Requirements

  -----------------------------------------------------------------------
  Table                  Status                    Notes
  ---------------------- ------------------------- ----------------------
  Users                  \[Complete\]              Full model with roles,
                                                   balance

  Offers/Needs           \[Complete\]              Separate models with
                                                   all fields

  TimeBankTransactions   \[Complete\]              Double-entry
  (LedgerEntry)                                    bookkeeping

  Comments (via Ratings) \[Complete\]              Rating model with
                                                   public comments

  Reports                \[Complete\]              Full report model

  Tags                   \[Complete\]              With semantic features

  Participants           \[Complete\]              Handshake/exchange
                                                   tracking

  UserBadges             \[Not Complete\]          No dedicated badge
                                                   table

  ForumTopics            \[Complete\]              Full forum model

  ForumComments          \[Complete\]              Comment model
  -----------------------------------------------------------------------

### 3.5.2 Design Constraints

  ------------------------------------------------------------------------
  Constraint                      Status                Notes
  ------------------------------- --------------------- ------------------
  Backend: Python (FastAPI)       \[Complete\]          FastAPI with
                                                        SQLModel

  Database: PostgreSQL            \[Complete\]          PostgreSQL 15

  Dockerized deployment           \[Complete\]          Full Docker setup

  Web-based frontend (HTML5, CSS, \[Complete\]          React +
  JS)                                                   TypeScript +
                                                        Material-UI

  REST APIs with JSON responses   \[Complete\]          OpenAPI/Swagger
                                                        documented
  ------------------------------------------------------------------------

------------------------------------------------------------------------

## Summary

### Overall Completion Rate

  Category               Complete   Partial   Not Complete   Total
  ---------------------- ---------- --------- -------------- --------
  FR-1 (Auth)            5          0         0              5
  FR-2 (Profile)         5          0         0              5
  FR-3 (Offers/Needs)    7          0         0              7
  FR-4 (Calendar)        2          1         0              3
  FR-5 (Handshake)       6          0         0              6
  FR-6 (Messaging)       0          0         3              3
  FR-7 (TimeBank)        4          1         1              6
  FR-8 (Tags/Search)     5          0         0              5
  FR-9 (Map)             4          0         0              4
  FR-10 (Feedback)       3          0         0              3
  FR-11 (Moderation)     4          0         0              4
  FR-12 (Archiving)      3          0         0              3
  FR-13 (Badges)         1          4         1              6
  FR-14 (Active Items)   4          0         0              4
  FR-15 (Forum)          6          0         0              6
  **TOTAL FR**           **59**     **6**     **5**          **70**
  NFR (Non-Functional)   6          5         2              13

### Key Missing Features

1.  **FR-6: Messaging System** - No direct messaging between
    participants
2.  **FR-7.7: Anti-hoarding rule** - Provider earns hours per exchange,
    not per session
3.  **FR-13: Full Badge System** - Frontend badges exist but no backend
    badge model or admin catalog
4.  **NFR-10: Database Backups** - No automated backup configuration
5.  **NFR-12: Maintenance Mode** - No maintenance page implementation

### Percentage Complete

-   **Functional Requirements**: 84% Complete (59/70), 9% Partial, 7%
    Not Complete
-   **Non-Functional Requirements**: 46% Complete, 38% Partial, 15% Not
    Complete
-   **Overall**: \~80% Complete

------------------------------------------------------------------------

# Status of Deployment

The project is dockerized and deployed on "hive.yusufss.com" server.

# Installation Guide

This guide provides step-by-step instructions for installing The Hive on
both local development and production environments using Docker Compose.

## Prerequisites

-   Docker Engine 20.10 or later
-   Docker Compose 2.0 or later
-   Git (to clone the repository)

Verify installation:

``` bash
docker --version
docker compose version
```

## Local Development Installation

### Step 1: Clone the Repository

``` bash
git clone <repository-url>
cd swe573-practice
```

### Step 2: Navigate to Infrastructure Directory

``` bash
cd the_hive/infra
```

### Step 3: Start Services

``` bash
docker compose up -d
```

This will start: - PostgreSQL database (port 5433) - FastAPI backend
(port 8000) - React frontend (port 5173)

### Step 4: Initialize Database

Wait for all services to be healthy, then initialize the database:

``` bash
docker compose exec backend python scripts/init_db.py
```

### Step 5: Seed Semantic Tags (Optional)

``` bash
docker compose exec backend python scripts/seed_semantic_tags.py
```

### Step 6: Access the Application

-   **Frontend**: http://localhost:5173
-   **Backend API**: http://localhost:8000
-   **API Documentation**: http://localhost:8000/docs

### Step 7: Verify Installation

Check that all containers are running:

``` bash
docker compose ps
```

All services should show "Up" status.

### Default Login Credentials

After database initialization: - **Regular users**: username `alice` (or
bob, carol, etc.), password `UserPass123!` - **Moderator**: username
`moderator`, password `ModeratorPass123!`

### Useful Commands

``` bash
# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v

# Restart a specific service
docker compose restart backend

# Rebuild after code changes
docker compose up -d --build
```

## Production Installation

### Step 1: Clone the Repository

``` bash
git clone <repository-url>
cd swe573-practice/the_hive/infra
```

### Step 2: Create Environment File

Create a `.env` file in the `infra` directory:

``` bash
nano .env
```

Add the following variables (adjust values for your environment):

``` env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password-here
POSTGRES_DB=the_hive

# Backend
DATABASE_URL=postgresql://postgres:your-secure-password-here@db:5432/the_hive
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ADMIN_SESSION_SECRET=your-admin-secret-here-generate-with-openssl-rand-hex-32
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
APP_ENV=production

# Frontend
VITE_API_BASE_URL=https://yourdomain.com/api/v1
VITE_MAP_DEFAULT_LAT=41.0082
VITE_MAP_DEFAULT_LNG=28.9784
VITE_MAP_DEFAULT_ZOOM=12
```

**Generate secure secrets:**

``` bash
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 32  # For ADMIN_SESSION_SECRET
```

### Step 3: Create Nginx Configuration

Create `nginx.prod.conf` in the `infra` directory with your domain
configuration.

### Step 4: Start Services

``` bash
docker compose -f docker-compose.prod.yml up -d --build
```

This will start: - PostgreSQL database - FastAPI backend - React
frontend (production build) - Nginx reverse proxy (ports 80 and 443)

### Step 5: Initialize Database

``` bash
docker compose -f docker-compose.prod.yml exec backend python scripts/init_db.py
```

### Step 6: Seed Semantic Tags

``` bash
docker compose -f docker-compose.prod.yml exec backend python scripts/seed_semantic_tags.py
```

### Step 7: Configure SSL (Recommended)

If using HTTPS, set up SSL certificates with Let's Encrypt and update
nginx configuration accordingly.

### Step 8: Verify Installation

Check container status:

``` bash
docker compose -f docker-compose.prod.yml ps
```

Test endpoints: - Frontend: http://yourdomain.com (or
https://yourdomain.com) - API: http://yourdomain.com/api/v1/health - API
Docs: http://yourdomain.com/docs

### Production Maintenance Commands

``` bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# View logs for specific service
docker compose -f docker-compose.prod.yml logs -f backend

# Stop services
docker compose -f docker-compose.prod.yml down

# Restart services
docker compose -f docker-compose.prod.yml restart

# Update application (after code changes)
docker compose -f docker-compose.prod.yml up -d --build

# Backup database
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres the_hive > backup_$(date +%Y%m%d).sql

# Restore database
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres the_hive < backup.sql
```

### Reset Everything

``` bash
# Stop and remove all containers, volumes, and networks
docker compose down -v

# Remove all images
docker compose down --rmi all

# Start fresh
docker compose up -d --build
```

# System Requirements

# AI Usage Declaration

This document declares all Artificial Intelligence (AI) tools used in
the development of **The Hive** time-banking platform.

## 1. Code Development

**Tools**: GitHub Copilot (with Claude 4.5), Cursor IDE

**Usage**: Code generation, autocomplete, refactoring suggestions,
debugging assistance, documentation comments

**Project References**: `the_hive/app/api/`, `the_hive/app/models/`,
`the_hive/app/schemas/`, `the_hive/frontend/src/components/`,
`the_hive/frontend/src/types/`, `the_hive/frontend/src/services/`,
`the_hive/tests/`

## 2. Documentation

**Tools**: Google Gemini, ChatGPT 5.1, Cursor IDE

**Usage & References**: SRS document generation, technical
documentation, README files, code docstrings, project documentation,
files in Wiki.

## 3. Design & UI/UX

**Tools**: Figma AI

**Usage**: Frontend mockups.

## 4. Content & Media

**Tools**: ChatGPT Image Generator (DALL-E)

**Usage**: User story images

# User Manual

Welcome to The Hive! This manual will guide you through using our
time-banking community platform where you can exchange services with
other community members using time as currency.

## Table of Contents

1.  [Getting Started](#getting-started)
2.  [Your Profile](#your-profile)
3.  [Creating Offers and Needs](#creating-offers-and-needs)
4.  [Finding Services](#finding-services)
5.  [Applying to Offers and Needs](#applying-to-offers-and-needs)
6.  [Managing Exchanges](#managing-exchanges)
7.  [Completing Exchanges](#completing-exchanges)
8.  [Rating System](#rating-system)
9.  [TimeBank System](#timebank-system)
10. [Community Forum](#community-forum)
11. [Search and Discovery](#search-and-discovery)
12. [Map View](#map-view)
13. [Notifications](#notifications)
14. [Frequently Asked Questions](#frequently-asked-questions)

------------------------------------------------------------------------

## Getting Started

### Creating an Account

1.  Click **"Register"** on the homepage
2.  Fill in your information:
    -   **Username**: Choose a unique username (minimum 3 characters)
    -   **Email**: Your email address
    -   **Password**: Create a secure password (minimum 8 characters)
    -   **Full Name**: Your display name
3.  Click **"Register"** to create your account

### Logging In

1.  Click **"Login"** on the homepage
2.  Enter your **Username** and **Password**
3.  Click **"Login"**

You'll be automatically logged in and redirected to your dashboard.

### Your Starting Balance

When you create an account, you receive **5 hours** in your TimeBank to
get started. This initial balance allows you to immediately request
services from other community members.

------------------------------------------------------------------------

## Your Profile

### Viewing Your Profile

Click on your username in the navigation bar or go to **"My Profile"**
to view your profile page.

### Profile Information

Your profile displays: - **Avatar**: Your profile picture (preset emoji
or custom image) - **Full Name**: Your display name - **About**: Your
bio/description - **Location**: Your city/neighborhood - **Tags**:
Skills and interests you've added - **Social Media Links**: Your blog,
Instagram, Facebook, Twitter profiles - **TimeBank Balance**: Your
current hours - **Statistics**: Hours given, hours received, ratings
received - **Badges**: Achievements you've earned

### Editing Your Profile

1.  Go to **"My Profile"**
2.  Click the **"Edit"** button
3.  Update any of the following:
    -   **Full Name**: Change your display name
    -   **About**: Update your bio
    -   **Tags**: Add or remove skill tags (maximum 10 tags)
    -   **Social Media**: Add links to your social profiles
4.  Click **"Save"** to update your profile

### Changing Your Avatar

1.  Click on your avatar on your profile page
2.  Choose from:
    -   **Preset Avatars**: Select from a collection of emoji avatars
    -   **Upload Image**: Upload your own profile picture
    -   **Remove Image**: Go back to preset avatar
3.  Click **"Save"** to update

### Viewing Other Users' Profiles

Click on any username throughout the application to view their profile.
You can see their: - Profile information and bio - TimeBank statistics -
Recent activities - Ratings they've received - Their offers and needs

------------------------------------------------------------------------

## Creating Offers and Needs

### Creating an Offer

An **Offer** is a service you're willing to provide to others.

1.  Click **"Create Offer"** in the navigation
2.  Fill in the details:
    -   **Title**: A clear, descriptive title (e.g., "Python Programming
        Tutoring")
    -   **Description**: Detailed description of what you're offering
    -   **Location**:
        -   Select **"Remote"** for online services
        -   Or enter a **location name** and select on the map for
            in-person services
    -   **TimeBank Hours**: How many hours you're charging (1-10 hours
        maximum)
    -   **Capacity**: How many people can participate (default: 1)
    -   **Tags**: Select relevant tags (e.g., "programming", "tutoring")
    -   **Time Slots** (Optional): Add specific dates and times you're
        available
3.  Click **"Create Offer"**

Your offer will be visible to all community members and will appear on
the map if it's location-based.

### Creating a Need

A **Need** is a service you're looking to receive.

1.  Click **"Create Need"** in the navigation
2.  Fill in the details:
    -   **Title**: What you need (e.g., "Help Moving Furniture")
    -   **Description**: Detailed description of what you need
    -   **Location**:
        -   Select **"Remote"** for online services
        -   Or enter a **location name** and select on the map for
            in-person services
    -   **TimeBank Hours**: How many hours you're willing to pay (1-10
        hours maximum)
        -   **Note**: You cannot create a need for more hours than your
            current TimeBank balance
    -   **Capacity**: How many people you need (default: 1)
    -   **Tags**: Select relevant tags
    -   **Time Slots** (Optional): Add specific dates and times you need
        help
3.  Click **"Create Need"**

### Managing Your Offers and Needs

Go to **"Active Items"** and select the **"My Posts"** tab to see: - All
your active offers and needs - Pending applications - Accepted
participants - Completed exchanges

You can: - **Edit**: Update details (if no one has applied yet) -
**Extend**: Extend the expiration date - **Delete**: Remove if no longer
needed

------------------------------------------------------------------------

## Finding Services

### Browse Active Items

1.  Click **"Active Items"** in the navigation
2.  Browse all available offers and needs
3.  Use filters to narrow down:
    -   **Type**: Show only Offers, only Needs, or Both
    -   **Tags**: Filter by specific tags
    -   **Remote/In-Person**: Filter by location type
4.  Click on any item to view details

### Using the Map

1.  Click **"Map"** in the navigation
2.  View offers and needs on an interactive map
3.  Click on map markers to see item details
4.  Filter by tags using the tag selector
5.  Items are sorted by distance from your location (if provided)

### Search

1.  Click **"Search"** in the navigation
2.  Enter keywords in the search box
3.  Filter by:
    -   **Type**: Offers, Needs, or Both
    -   **Tags**: Select one or more tags
    -   **Remote**: Show only remote or in-person items
4.  Results are sorted by relevance and recency

------------------------------------------------------------------------

## Applying to Offers and Needs

### Applying to an Offer

When you find an offer you're interested in:

1.  Click on the offer to view details
2.  Review:
    -   Service description
    -   TimeBank hours required
    -   Capacity and availability
    -   Time slots (if available)
    -   Provider's profile and ratings
3.  Click **"Request Service"**
4.  Write a message explaining:
    -   Why you're interested
    -   What makes you a good fit
    -   Your relevant experience
5.  Select time slots (if the offer has them)
6.  Click **"Send Request"**

**Important**: You must have enough TimeBank hours in your balance to
apply. The system will check your balance before allowing the
application.

### Applying to a Need

When you find a need you can help with:

1.  Click on the need to view details
2.  Review the requirements
3.  Click **"Propose to Help"**
4.  Write a message explaining:
    -   How you can help
    -   Your relevant skills or experience
    -   Your availability
5.  Select time slots (if the need has them)
6.  Click **"Send Proposal"**

### Viewing Your Applications

Go to **"Active Items"** and select the **"My Applications"** tab to
see: - All offers and needs you've applied to - Status of each
application (Pending, Accepted, Declined) - Messages and updates

------------------------------------------------------------------------

## Managing Exchanges

### For Offer Creators

When someone applies to your offer:

1.  Go to **"Active Items"** -\> **"My Posts"**
2.  Find the offer with new applications
3.  Click to view applicants
4.  For each applicant, you can:
    -   **Accept**: Approve their application
    -   **Decline**: Reject their application
    -   **View Profile**: See their profile and ratings

Once accepted, the participant can see the exchange in their "My
Applications" tab.

### For Need Creators

When someone proposes to help with your need:

1.  Go to **"Active Items"** -\> **"My Posts"**
2.  Find the need with proposals
3.  Review each proposal
4.  Accept or decline as appropriate

### Capacity Limits

-   Offers and needs have a **capacity** (maximum number of
    participants)
-   Once capacity is reached, the item is marked as **"Full"**
-   No new applications can be accepted when full
-   You can still see pending applications even when full

------------------------------------------------------------------------

## Completing Exchanges

### Confirming Completion

After an exchange is completed, both parties must confirm:

1.  Go to **"Active Items"** -\> **"My Posts"** or **"My Applications"**
2.  Find the completed exchange
3.  Click **"Complete Exchange"**
4.  Confirm that the service was completed

**Important**: Both parties must confirm before TimeBank hours are
transferred.

### What Happens When Both Confirm

-   **For Offers**: You (the provider) receive hours, the requester pays
    hours
-   **For Needs**: You (the requester) pay hours, the provider receives
    hours
-   Both balances are updated automatically
-   You can now rate each other

### If Only One Party Confirms

-   The exchange shows as **"Awaiting Confirmation"**
-   A notification is sent to the other party
-   Hours are not transferred until both confirm

------------------------------------------------------------------------

## Rating System

### Leaving a Rating

After both parties confirm an exchange:

1.  You'll receive a notification to rate the other party
2.  Go to the exchange details
3.  Click **"Submit Rating"**
4.  Rate on three categories (1-5 stars each):
    -   **Reliability & Commitment**: Punctuality, communication,
        follow-through
    -   **Kindness & Respect**: Politeness, comfort, mutual respect
    -   **Helpfulness & Support**: Meaningfulness and supportiveness
5.  Optionally add a **public comment** (visible on their profile)
6.  Click **"Submit Rating"**

### Blind Rating System

Ratings are **blind** - they remain hidden until: - Both parties have
submitted their ratings, OR - 7 days have passed since the exchange
completion

This encourages honest, unbiased feedback.

### Viewing Ratings

-   **On Profiles**: Visit any user's profile to see their visible
    ratings
-   **Rating Averages**: See average scores for each category
-   **Rating Distribution**: See how many 1-star, 2-star, etc. ratings
    they have

------------------------------------------------------------------------

## TimeBank System

### Understanding Your Balance

-   **Balance**: Your current available hours
-   **Hours Given**: Total hours you've provided to others
-   **Hours Received**: Total hours you've received from others

### How Hours Work

-   **Earning Hours**: When you provide a service (offer), you earn
    hours
-   **Spending Hours**: When you receive a service (need or request an
    offer), you spend hours
-   **Starting Balance**: New users start with 5 hours
-   **Reciprocity Limit**: You can go up to 10 hours in debt (negative
    balance) to encourage participation

### Viewing Your Transaction History

1.  Go to **"My Profile"**
2.  Scroll to **"TimeBank Statistics"**
3.  View your balance and transaction summary
4.  Click to see detailed ledger history

### Transaction Types

-   **Initial**: Your starting 5-hour balance
-   **Exchange**: Hours transferred during completed exchanges
-   **Credit**: Hours you earned
-   **Debit**: Hours you spent

------------------------------------------------------------------------

## Community Forum

### Viewing the Forum

1.  Click **"Forum"** in the navigation
2.  Browse discussion topics and events
3.  Filter by:
    -   **Type**: Discussions or Events
    -   **Tags**: Filter by topic tags
    -   **Search**: Find specific topics

### Creating a Discussion Topic

1.  Click **"New Topic"** in the Forum
2.  Select **"Discussion"**
3.  Enter:
    -   **Title**: Topic title
    -   **Content**: Your message
    -   **Tags**: Relevant tags
4.  Click **"Create Topic"**

### Creating an Event

1.  Click **"New Topic"** in the Forum
2.  Select **"Event"**
3.  Enter:
    -   **Title**: Event name
    -   **Description**: Event details
    -   **Start Time**: When the event begins
    -   **End Time**: When the event ends
    -   **Location**: Where the event takes place
    -   **Tags**: Relevant tags
4.  Optionally link to an offer or need
5.  Click **"Create Event"**

### Participating in Discussions

-   **Comment**: Click on any topic to view and add comments
-   **Reply**: Engage with other community members
-   **Edit**: Edit your own comments
-   **Delete**: Remove your own comments

------------------------------------------------------------------------

## Search and Discovery

### Using Search

1.  Click **"Search"** in the navigation
2.  Enter keywords (e.g., "programming", "cooking", "gardening")
3.  Results show matching offers and needs
4.  Use filters to narrow results:
    -   **Type**: Offers, Needs, or Both
    -   **Tags**: Select specific tags
    -   **Remote**: Filter by location type
    -   **Sort**: By recency or relevance

### Tag System

-   **Browse Tags**: Click **"Tags"** to see all available tags
-   **Tag Hierarchy**: Some tags have parent-child relationships
-   **Tag Details**: Click any tag to see:
    -   Description
    -   Related tags
    -   Items using this tag
    -   "View on Map" button

### Tag Autocomplete

When creating offers/needs or searching: - Start typing a tag name -
Suggestions appear automatically - Tags are created on-demand if they
don't exist

------------------------------------------------------------------------

## Map View

### Using the Map

1.  Click **"Map"** in the navigation
2.  View all location-based offers and needs
3.  **Map Features**:
    -   Zoom in/out
    -   Pan to different areas
    -   Click markers to see item details
    -   Filter by tags
    -   See distance from your location

### Privacy on the Map

-   **Approximate Locations**: Exact addresses are never shown
-   **Rounded Coordinates**: Locations are rounded to protect privacy
-   **Remote Items**: Remote offers/needs don't appear on the map

### Distance Calculation

-   If you've set your location, distances are calculated automatically
-   Items are sorted by distance (closest first)
-   Remote items appear at the end of the list

------------------------------------------------------------------------

## Notifications

### Notification Types

You'll receive notifications for: - **New Application**: Someone applied
to your offer/need - **Application Accepted**: Your application was
accepted - **Application Declined**: Your application was declined -
**Exchange Completed**: An exchange you participated in was completed -
**Exchange Awaiting Confirmation**: Other party confirmed, waiting for
you - **Rating Received**: Someone rated you - **Participant
Cancelled**: A participant cancelled their participation

### Viewing Notifications

1.  Click the **bell icon** in the navigation bar
2.  See all your notifications
3.  Unread notifications are highlighted
4.  Click any notification to view details

### Notification Actions

-   **Mark as Read**: Click on a notification to mark it read
-   **Mark All as Read**: Button to clear all notifications
-   **Navigate**: Clicking notifications takes you to relevant pages

------------------------------------------------------------------------

## Frequently Asked Questions

### General Questions

**Q: What is time banking?** A: Time banking is a system where you
exchange services using time as currency. When you help someone, you
earn hours. When someone helps you, you spend hours.

**Q: How do I get started?** A: Create an account, set up your profile,
and start browsing offers and needs in your community!

**Q: What if I don't have enough hours?** A: You can go up to 10 hours
in debt (negative balance) to encourage participation. Focus on
providing services to earn hours back.

### Offers and Needs

**Q: What's the difference between an Offer and a Need?** A: An
**Offer** is a service you're providing. A **Need** is a service you're
looking to receive.

**Q: Can I edit my offer/need after creating it?** A: Yes, you can edit
offers and needs that don't have any applications yet. Once someone
applies, you can only extend the expiration date.

**Q: What happens when my offer/need expires?** A: Expired items are
automatically archived. You can create a new one or renew the expired
item.

**Q: How many hours can I charge?** A: The maximum is 10 hours per offer
or need.

### Applications and Exchanges

**Q: Can I apply to multiple offers/needs?** A: Yes! You can apply to as
many as you want, as long as you have enough hours in your balance.

**Q: What if I need to cancel after being accepted?** A: You can cancel
your participation, but this may affect your ratings. Communicate with
the other party first.

**Q: How long do I have to complete an exchange?** A: There's no strict
deadline, but it's good practice to complete exchanges in a timely
manner. The item expiration date gives a general timeframe.

### Ratings

**Q: When can I rate someone?** A: You can rate after both parties have
confirmed the exchange completion.

**Q: Can I change my rating?** A: No, ratings cannot be edited once
submitted. Make sure you're satisfied with your rating before
submitting.

**Q: Why can't I see a rating I received?** A: Ratings are "blind" -
they're hidden until both parties rate or 7 days pass. This encourages
honest feedback.

### TimeBank

**Q: What happens to my hours if an exchange is cancelled?** A: Hours
are only transferred when both parties confirm completion. If cancelled
before completion, no hours are transferred.

**Q: Can I transfer hours to another user?** A: No, hours can only be
earned or spent through completed exchanges.

**Q: What's the reciprocity limit?** A: You can go up to 10 hours in
debt (negative balance) to encourage participation. Once you reach -10
hours, you must earn hours before requesting more services.

### Technical Issues

**Q: I can't log in. What should I do?** A: Check that you're using the
correct username (not email) and password. If you forgot your password,
contact support.

**Q: The map isn't showing my location.** A: Make sure you've set your
location in your profile settings.

**Q: Notifications aren't appearing.** A: Check your browser's
notification permissions. Also ensure you're logged in and have an
active internet connection.

------------------------------------------------------------------------

## Tips for Success

1.  **Complete Your Profile**: Add a bio, tags, and location to help
    others find you
2.  **Be Clear in Descriptions**: Detailed descriptions help others
    understand what you're offering or need
3.  **Communicate Promptly**: Respond to applications and messages
    quickly
4.  **Set Realistic Expectations**: Be honest about your skills and
    availability
5.  **Leave Thoughtful Ratings**: Helpful ratings benefit the entire
    community
6.  **Participate in the Forum**: Engage with the community to build
    connections
7.  **Use Tags Wisely**: Relevant tags help others discover your offers
    and needs
8.  **Respect Time Slots**: If you set time slots, honor them or update
    them promptly

------------------------------------------------------------------------

## Getting Help

-   **Community Forum**: Ask questions and get help from other members
-   **Report Issues**: Use the report button to flag inappropriate
    content
-   **Contact Support**: Reach out through the platform for technical
    assistance

------------------------------------------------------------------------

**Welcome to The Hive! We're excited to have you in our community. Happy
time banking!**

# Use Case

## Use Case: Finding a Piano Tuner through The Hive

### Title

Finding and Engaging a Piano Tuner for Vintage Piano Maintenance

### Actors

-   **Primary Actor**: Requester (User seeking piano tuning service)
-   **Secondary Actor**: Provider (Mert - Piano mechanic offering tuning
    services)

### Brief Description

A user needs to tune a vintage upright piano received from their
grandmother. The piano is out of tune and the keys are hard to press.
The user wants to find a piano mechanic who can tune the piano and
potentially teach them how to maintain it. Through The Hive platform,
the user discovers Mert, a local musician and piano mechanic, and
successfully arranges for the piano tuning service.

### Preconditions

1.  Both actors are registered users of The Hive platform
2.  The requester has a TimeBank balance sufficient to pay for the
    service (at least the number of hours required)
3.  The provider (Mert) has created an Offer for piano
    tuning/maintenance services
4.  The provider's offer includes relevant tags such as "piano tuning",
    "piano repair", or "music instruments"

### Main Success Scenario

1.  **Requester creates a Need**: The requester logs into The Hive and
    creates a Need post describing:

    -   Title: "Piano Tuning and Maintenance Help"
    -   Description: Details about the vintage upright piano that needs
        tuning and key maintenance, and desire to learn maintenance
        skills
    -   Location: Approximate location or marked as in-person service
    -   Tags: "piano tuning", "piano repair", "music instruments",
        "maintenance"
    -   TimeBank hours: Specifies how many hours they're willing to pay
        (e.g., 3-5 hours)

2.  **Provider discovers the Need**: Mert, a piano mechanic, browses The
    Hive using the map or search functionality, filters by relevant
    tags, and discovers the requester's Need for piano tuning.

3.  **Provider proposes to help**: Mert views the Need details, reviews
    the requester's profile and ratings, then clicks "Propose to Help"
    with an optional message explaining:

    -   His experience with piano tuning and repair
    -   His background at the local music shop
    -   His willingness to teach maintenance skills
    -   His availability

4.  **Requester reviews proposals**: The requester receives a
    notification about the new proposal. They view Mert's proposal in
    the "Active Items" -\> "My Posts" section, review Mert's profile,
    ratings, and previous work history.

5.  **Requester accepts proposal**: The requester finds Mert's proposal
    suitable, clicks "Accept" to confirm the exchange. The exchange
    status changes to "Accepted" and becomes active.

6.  **Communication and coordination**: Both parties use the messaging
    system to:

    -   Coordinate a suitable time for the service
    -   Discuss specific details about the piano's condition
    -   Arrange logistics (address, tools needed, etc.)

7.  **Service delivery**: Mert visits the requester's location and:

    -   Tunes the vintage upright piano
    -   Repairs/adjusts the keys that are hard to press
    -   Teaches the requester basic piano maintenance skills

8.  **Exchange completion**: After the service is completed:

    -   Both parties confirm completion through The Hive
    -   TimeBank hours are automatically transferred (requester pays
        hours, provider earns hours)
    -   Exchange status changes to "Completed"

9.  **Rating and feedback**: Both parties leave ratings for each other:

    -   Requester rates Mert on Reliability, Kindness, and Helpfulness
    -   Provider rates the requester on the same categories
    -   Optional public comments are added to each other's profiles

### Postconditions

1.  The vintage piano is tuned and keys are repaired/adjusted
2.  The requester has learned basic piano maintenance skills from the
    provider
3.  TimeBank hours have been transferred (requester debited, provider
    credited)
4.  Both parties have completed ratings for each other
5.  The exchange appears in both parties' completed exchange history
6.  Ratings and comments are visible on both parties' public profiles
    (after blind rating period)
7.  The grandmother will be pleased to hear the piano sounding like it
    did in her younger days

### Success Criteria

-   Piano is successfully tuned and maintained
-   Requester learns maintenance skills as desired
-   Both parties are satisfied with the exchange
-   TimeBank transaction completes successfully
-   Community connection is established (requester now knows someone
    from a local music shop)
-   Platform facilitates skill sharing and community building

# Test Plan

## Test Categories

### 1. Authentication & Authorization Tests (`test_auth.py`, `test_rbac.py`)

-   User registration (validation, duplicate checks)
-   Login/logout
-   Password hashing
-   JWT token handling
-   Profile updates
-   Role-based access control (User/Moderator/Admin)
-   Permission checks

### 2. Core Feature Tests

**Offers & Needs** (`test_offers.py`, `test_needs.py`) - CRUD
operations - Location validation - Capacity management - Status
transitions - Expiration handling

**Handshake/Proposals** (`test_handshake.py`) - Proposing help for
offers/needs - Accepting/rejecting proposals - Capacity limits - Status
workflows

**Participants** (`test_participants.py`) - Applying to offers/needs -
Accepting participants - Capacity enforcement - Role management

### 3. Business Logic Tests

**TimeBank Ledger** (`test_ledger.py`) - Double-entry bookkeeping -
Balance updates - Reciprocity limit (10-hour debt limit) - Transaction
audit trail - Exchange completion - Balance integrity verification

**Ratings** (`test_ratings.py`) - Creating ratings (multi-category) -
Blind rating system (visibility control) - Rating visibility deadlines -
Rating retrieval and display

### 4. Integration & Workflow Tests

**Golden Path** (`test_golden_path_need.py`) - End-to-end workflows -
Complete exchange scenarios - Reciprocity limit in real scenarios

### 5. Feature-Specific Tests

**Forum** (`test_forum.py`) - Discussion topics - Event topics -
Comments - Tag associations - Search and filtering

**Search** (`test_search.py`) - Text search - Tag filtering - Type
filtering (offers/needs) - Pagination - Tag autocomplete

**Map** (`test_map.py`) - Location approximation (privacy) - Distance
calculations - Sorting by distance - Tag filtering on map - Remote vs
in-person items

**Notifications** (`test_notifications.py`) - Notification creation -
Marking as read - Pagination - Different notification types - WebSocket
integration

**Moderation** (`test_moderation.py`) - Reporting system - Moderator
actions (suspend, ban, remove content) - Report filtering and stats -
Permission checks

**Time Slots** (`test_time_slots.py`) - Creating offers/needs with time
slots - Time slot validation - Date/time format validation

**Social Media** (`test_social_media.py`) - Social media profile links -
Validation

### 6. Infrastructure Tests

**Health Checks** (`test_health.py`) - API health endpoint - Root
endpoint

**User Timezone** (`test_user_timezone.py`) - Timezone handling

## Test Characteristics

-   Framework: pytest with FastAPI TestClient
-   Database: In-memory SQLite for isolation
-   Type: Unit and integration tests
-   Coverage: 217 tests across 19 test files
-   Focus: API endpoints, business logic, data validation, security

These tests cover core functionality, business rules, security, and edge
cases.

## Test Output

``` bash
=================================================================================== test session starts ====================================================================================
platform linux -- Python 3.11.14, pytest-9.0.1, pluggy-1.6.0 -- /usr/local/bin/python3.11
cachedir: .pytest_cache
rootdir: /app
configfile: pyproject.toml
plugins: anyio-4.12.0, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 217 items

tests/test_auth.py::test_register_user PASSED                                                                                                                                        [  0%]
tests/test_auth.py::test_register_duplicate_username PASSED                                                                                                                          [  0%]
tests/test_auth.py::test_register_duplicate_email PASSED                                                                                                                             [  1%]
tests/test_auth.py::test_register_invalid_email PASSED                                                                                                                               [  1%]
tests/test_auth.py::test_register_short_username PASSED                                                                                                                              [  2%]
tests/test_auth.py::test_register_short_password PASSED                                                                                                                              [  2%]
tests/test_auth.py::test_login_success PASSED                                                                                                                                        [  3%]
tests/test_auth.py::test_login_wrong_password PASSED                                                                                                                                 [  3%]
tests/test_auth.py::test_login_nonexistent_user PASSED                                                                                                                               [  4%]
tests/test_auth.py::test_login_inactive_user PASSED                                                                                                                                  [  4%]
tests/test_auth.py::test_get_current_user_with_token PASSED                                                                                                                          [  5%]
tests/test_auth.py::test_get_current_user_without_token PASSED                                                                                                                       [  5%]
tests/test_auth.py::test_get_current_user_invalid_token PASSED                                                                                                                       [  5%]
tests/test_auth.py::test_logout PASSED                                                                                                                                               [  6%]
tests/test_auth.py::test_password_hashing PASSED                                                                                                                                     [  6%]
tests/test_auth.py::test_user_roles PASSED                                                                                                                                           [  7%]
tests/test_auth.py::test_update_profile PASSED                                                                                                                                       [  7%]
tests/test_auth.py::test_update_profile_tags_limit PASSED                                                                                                                            [  8%]
tests/test_auth.py::test_update_profile_invalid_preset_avatar PASSED                                                                                                                 [  8%]
tests/test_auth.py::test_get_preset_avatars PASSED                                                                                                                                   [  9%]
tests/test_auth.py::test_profile_includes_tags PASSED                                                                                                                                [  9%]
tests/test_forum.py::test_create_discussion_topic PASSED                                                                                                                             [ 10%]
tests/test_forum.py::test_create_event_topic PASSED                                                                                                                                  [ 10%]
tests/test_forum.py::test_create_topic_invalid_type PASSED                                                                                                                           [ 11%]
tests/test_forum.py::test_link_offer_to_event PASSED                                                                                                                                 [ 11%]
tests/test_forum.py::test_link_need_to_event PASSED                                                                                                                                  [ 11%]
tests/test_forum.py::test_cannot_link_both_offer_and_need PASSED                                                                                                                     [ 12%]
tests/test_forum.py::test_bidirectional_links PASSED                                                                                                                                 [ 12%]
tests/test_forum.py::test_list_topics PASSED                                                                                                                                         [ 13%]
tests/test_forum.py::test_filter_by_topic_type PASSED                                                                                                                                [ 13%]
tests/test_forum.py::test_search_by_keyword PASSED                                                                                                                                   [ 14%]
tests/test_forum.py::test_filter_by_tags PASSED                                                                                                                                      [ 14%]
tests/test_forum.py::test_events_ordered_by_recency PASSED                                                                                                                           [ 15%]
tests/test_forum.py::test_get_topic PASSED                                                                                                                                           [ 15%]
tests/test_forum.py::test_update_topic PASSED                                                                                                                                        [ 16%]
tests/test_forum.py::test_only_creator_can_update PASSED                                                                                                                             [ 16%]
tests/test_forum.py::test_delete_topic PASSED                                                                                                                                        [ 17%]
tests/test_forum.py::test_create_comment PASSED                                                                                                                                      [ 17%]
tests/test_forum.py::test_list_comments PASSED                                                                                                                                       [ 17%]
tests/test_forum.py::test_update_comment PASSED                                                                                                                                       [ 18%]
tests/test_forum.py::test_delete_comment PASSED                                                                                                                                      [ 18%]
tests/test_forum.py::test_comment_count_increments PASSED                                                                                                                            [ 19%]
tests/test_forum.py::test_pagination PASSED                                                                                                                                          [ 19%]
tests/test_golden_path_need.py::test_golden_path_complete_need_workflow PASSED                                                                                                       [ 20%]
tests/test_golden_path_need.py::test_golden_path_with_reciprocity_limit_check PASSED                                                                                                 [ 20%]
tests/test_handshake.py::test_propose_help_for_offer PASSED                                                                                                                          [ 21%]
tests/test_handshake.py::test_propose_help_for_need PASSED                                                                                                                           [ 21%]
tests/test_handshake.py::test_propose_without_message PASSED                                                                                                                         [ 22%]
tests/test_handshake.py::test_accept_handshake_by_requester PASSED                                                                                                                   [ 22%]
tests/test_handshake.py::test_only_requester_can_accept PASSED                                                                                                                       [ 23%]
tests/test_handshake.py::test_cannot_accept_if_full PASSED                                                                                                                           [ 23%]
tests/test_handshake.py::test_cannot_propose_if_already_full PASSED                                                                                                                  [ 23%]
tests/test_handshake.py::test_proposer_sees_pending_until_accepted PASSED                                                                                                            [ 24%]
tests/test_handshake.py::test_requester_sees_pending_proposals PASSED                                                                                                                [ 24%]
tests/test_handshake.py::test_handshake_increments_accepted_count PASSED                                                                                                             [ 25%]
tests/test_handshake.py::test_need_handshake_workflow PASSED                                                                                                                         [ 25%]
tests/test_health.py::test_health_check PASSED                                                                                                                                       [ 26%]
tests/test_health.py::test_root_endpoint PASSED                                                                                                                                      [ 26%]
tests/test_ledger.py::test_complete_exchange_offer_double_entry_bookkeeping PASSED                                                                                                   [ 27%]
tests/test_ledger.py::test_complete_exchange_need_double_entry_bookkeeping PASSED                                                                                                    [ 27%]
tests/test_ledger.py::test_complete_exchange_balance_updates PASSED                                                                                                                  [ 28%]
tests/test_ledger.py::test_complete_exchange_creates_transfer_record PASSED                                                                                                          [ 28%]
tests/test_ledger.py::test_complete_exchange_marks_participant_completed PASSED                                                                                                      [ 29%]
tests/test_ledger.py::test_complete_exchange_partial_confirmation PASSED                                                                                                             [ 29%]
tests/test_ledger.py::test_complete_exchange_ledger_audit_trail PASSED                                                                                                               [ 29%]
tests/test_ledger.py::test_complete_exchange_only_accepted_status PASSED                                                                                                             [ 30%]
tests/test_ledger.py::test_check_reciprocity_limit_allows_positive_balance PASSED                                                                                                    [ 30%]
tests/test_ledger.py::test_check_reciprocity_limit_allows_within_limit PASSED                                                                                                        [ 31%]
tests/test_ledger.py::test_check_reciprocity_limit_warns_at_80_percent PASSED                                                                                                        [ 31%]
tests/test_ledger.py::test_check_reciprocity_limit_blocks_at_limit PASSED                                                                                                            [ 32%]
tests/test_ledger.py::test_check_reciprocity_limit_blocks_exactly_at_limit PASSED                                                                                                    [ 32%]
tests/test_ledger.py::test_verify_balance_integrity_valid PASSED                                                                                                                     [ 33%]
tests/test_ledger.py::test_verify_balance_integrity_detects_mismatch PASSED                                                                                                          [ 33%]
tests/test_ledger.py::test_complete_exchange_prevents_concurrent_completion PASSED                                                                                                   [ 34%]
tests/test_ledger.py::test_complete_exchange_multiple_exchanges_cumulative_balance PASSED                                                                                            [ 34%]
tests/test_ledger.py::test_ledger_history_endpoint_integration PASSED                                                                                                                [ 35%]
tests/test_ledger.py::test_ledger_pagination PASSED                                                                                                                                  [ 35%]
tests/test_map.py::test_approximate_coordinate_rounds_to_two_decimals PASSED                                                                                                         [ 35%]
tests/test_map.py::test_map_feed_returns_approximate_coords_not_exact PASSED                                                                                                         [ 36%]
tests/test_map.py::test_map_feed_never_exposes_exact_location PASSED                                                                                                                 [ 36%]
tests/test_map.py::test_haversine_distance_calculation PASSED                                                                                                                        [ 37%]
tests/test_map.py::test_map_feed_calculates_distance_when_user_location_provided PASSED                                                                                              [ 37%]
tests/test_map.py::test_map_feed_sorts_by_distance PASSED                                                                                                                            [ 38%]
tests/test_map.py::test_map_feed_remote_items_have_no_distance PASSED                                                                                                                [ 38%]
tests/test_map.py::test_map_feed_remote_items_sorted_last PASSED                                                                                                                     [ 39%]
tests/test_map.py::test_map_feed_returns_only_active_items PASSED                                                                                                                    [ 39%]
tests/test_map.py::test_map_feed_filters_by_tags PASSED                                                                                                                              [ 40%]
tests/test_map.py::test_map_feed_filters_by_multiple_tags PASSED                                                                                                                     [ 40%]
tests/test_map.py::test_map_feed_includes_both_offers_and_needs PASSED                                                                                                               [ 41%]
tests/test_map.py::test_map_feed_pagination PASSED                                                                                                                                   [ 41%]
tests/test_map.py::test_map_feed_response_includes_user_location PASSED                                                                                                              [ 41%]
tests/test_map.py::test_map_feed_works_without_user_location PASSED                                                                                                                  [ 42%]
tests/test_moderation.py::test_user_can_report_user PASSED                                                                                                                           [ 42%]
tests/test_moderation.py::test_user_can_report_offer PASSED                                                                                                                          [ 43%]
tests/test_moderation.py::test_user_can_report_need PASSED                                                                                                                           [ 43%]
tests/test_moderation.py::test_user_can_report_comment PASSED                                                                                                                        [ 44%]
tests/test_moderation.py::test_cannot_report_without_item PASSED                                                                                                                     [ 44%]
tests/test_moderation.py::test_cannot_self_report PASSED                                                                                                                             [ 45%]
tests/test_moderation.py::test_moderator_can_list_reports PASSED                                                                                                                     [ 45%]
tests/test_moderation.py::test_moderator_can_filter_reports PASSED                                                                                                                   [ 46%]
tests/test_moderation.py::test_moderator_can_get_report_stats PASSED                                                                                                                 [ 46%]
tests/test_moderation.py::test_moderator_can_resolve_report PASSED                                                                                                                   [ 47%]
tests/test_moderation.py::test_moderator_can_remove_offer PASSED                                                                                                                     [ 47%]
tests/test_moderation.py::test_moderator_can_remove_need PASSED                                                                                                                      [ 47%]
tests/test_moderation.py::test_moderator_can_remove_comment PASSED                                                                                                                   [ 48%]
tests/test_moderation.py::test_moderator_can_suspend_user PASSED                                                                                                                     [ 48%]
tests/test_moderation.py::test_moderator_can_ban_user PASSED                                                                                                                         [ 49%]
tests/test_moderation.py::test_cannot_suspend_moderator PASSED                                                                                                                       [ 49%]
tests/test_moderation.py::test_cannot_self_suspend PASSED                                                                                                                            [ 50%]
tests/test_moderation.py::test_moderator_can_unsuspend_user PASSED                                                                                                                   [ 50%]
tests/test_moderation.py::test_regular_user_cannot_access_moderation PASSED                                                                                                          [ 51%]
tests/test_needs.py::test_create_need_remote PASSED                                                                                                                                  [ 51%]
tests/test_needs.py::test_create_need_with_location PASSED                                                                                                                           [ 52%]
tests/test_needs.py::test_list_needs PASSED                                                                                                                                          [ 52%]
tests/test_needs.py::test_extend_need PASSED                                                                                                                                         [ 52%]
tests/test_needs.py::test_update_need PASSED                                                                                                                                         [ 53%]
tests/test_needs.py::test_delete_need PASSED                                                                                                                                         [ 53%]
tests/test_notifications.py::test_list_notifications_empty PASSED                                                                                                                    [ 54%]
tests/test_notifications.py::test_create_notification_helper PASSED                                                                                                                  [ 54%]
tests/test_notifications.py::test_list_notifications_with_data PASSED                                                                                                                [ 55%]
tests/test_notifications.py::test_mark_notification_as_read PASSED                                                                                                                   [ 55%]
tests/test_notifications.py::test_mark_notification_as_read_already_read PASSED                                                                                                      [ 56%]
tests/test_notifications.py::test_mark_notification_as_read_not_found PASSED                                                                                                         [ 56%]
tests/test_notifications.py::test_mark_notification_as_read_wrong_user PASSED                                                                                                        [ 57%]
tests/test_notifications.py::test_mark_all_as_read PASSED                                                                                                                            [ 57%]
tests/test_notifications.py::test_notification_pagination PASSED                                                                                                                     [ 58%]
tests/test_notifications.py::test_notification_filter_unread_only PASSED                                                                                                             [ 58%]
tests/test_notifications.py::test_notify_application_received PASSED                                                                                                                 [ 58%]
tests/test_notifications.py::test_notify_application_accepted PASSED                                                                                                                 [ 59%]
tests/test_notifications.py::test_notify_exchange_completed PASSED                                                                                                                   [ 59%]
tests/test_notifications.py::test_notify_exchange_awaiting_confirmation PASSED                                                                                                       [ 60%]
tests/test_notifications.py::test_notify_rating_received PASSED                                                                                                                      [ 60%]
tests/test_notifications.py::test_notification_related_entities PASSED                                                                                                               [ 61%]
tests/test_notifications.py::test_notification_types PASSED                                                                                                                          [ 61%]
tests/test_notifications.py::test_notification_unauthorized PASSED                                                                                                                   [ 62%]
tests/test_notifications.py::test_notification_ordering PASSED                                                                                                                       [ 62%]
tests/test_offers.py::test_create_offer_remote PASSED                                                                                                                                [ 63%]
tests/test_offers.py::test_create_offer_with_location PASSED                                                                                                                         [ 63%]
tests/test_offers.py::test_create_offer_missing_location PASSED                                                                                                                      [ 64%]
tests/test_offers.py::test_list_offers PASSED                                                                                                                                        [ 64%]
tests/test_offers.py::test_list_my_offers PASSED                                                                                                                                     [ 64%]
tests/test_offers.py::test_get_offer PASSED                                                                                                                                          [ 65%]
tests/test_offers.py::test_update_offer PASSED                                                                                                                                       [ 65%]
tests/test_offers.py::test_cannot_decrease_capacity_below_accepted PASSED                                                                                                            [ 66%]
tests/test_offers.py::test_extend_offer PASSED                                                                                                                                       [ 66%]
tests/test_offers.py::test_renew_expired_offer PASSED                                                                                                                                [ 67%]
tests/test_offers.py::test_delete_offer PASSED                                                                                                                                       [ 67%]
tests/test_offers.py::test_cannot_update_others_offer PASSED                                                                                                                         [ 68%]
tests/test_offers.py::test_pagination PASSED                                                                                                                                         [ 68%]
tests/test_participants.py::test_offer_help_for_offer PASSED                                                                                                                         [ 69%]
tests/test_participants.py::test_offer_help_for_need PASSED                                                                                                                          [ 69%]
tests/test_participants.py::test_cannot_offer_help_to_own_offer PASSED                                                                                                               [ 70%]
tests/test_participants.py::test_accept_participant_for_offer PASSED                                                                                                                 [ 70%]
tests/test_participants.py::test_offer_marked_full_when_capacity_reached PASSED                                                                                                      [ 70%]
tests/test_participants.py::test_cannot_exceed_capacity PASSED                                                                                                                       [ 71%]
tests/test_participants.py::test_concurrent_accepts_dont_exceed_capacity SKIPPED (SQLite in-memory doesn't support proper concurrent transactions. Test passes with PostgreSQL.)     [ 71%]
tests/test_participants.py::test_only_creator_can_accept_participants PASSED                                                                                                         [ 72%]
tests/test_participants.py::test_list_offer_participants PASSED                                                                                                                      [ 72%]
tests/test_participants.py::test_need_acceptance_flow PASSED                                                                                                                         [ 73%]
tests/test_ratings.py::TestCreateRating::test_create_rating_with_all_categories PASSED                                                                                               [ 73%]
tests/test_ratings.py::TestCreateRating::test_create_rating_with_all_categories_and_comment PASSED                                                                                   [ 74%]
tests/test_ratings.py::TestCreateRating::test_create_rating_missing_required_category PASSED                                                                                         [ 74%]
tests/test_ratings.py::TestCreateRating::test_create_rating_invalid_category_rating PASSED                                                                                           [ 75%]
tests/test_ratings.py::TestCreateRating::test_cannot_rate_invalid_recipient PASSED                                                                                                   [ 75%]
tests/test_ratings.py::TestCreateRating::test_cannot_rate_incomplete_exchange PASSED                                                                                                 [ 76%]
tests/test_ratings.py::TestCreateRating::test_cannot_rate_twice PASSED                                                                                                               [ 76%]
tests/test_ratings.py::TestBlindRatings::test_rating_status_before_submission PASSED                                                                                                 [ 76%]
tests/test_ratings.py::TestBlindRatings::test_rating_status_after_one_submission PASSED                                                                                              [ 77%]
tests/test_ratings.py::TestBlindRatings::test_rating_visible_after_both_submit PASSED                                                                                                [ 77%]
tests/test_ratings.py::TestGetRatings::test_get_user_ratings_visible_only PASSED                                                                                                     [ 78%]
tests/test_ratings.py::TestGetRatings::test_get_exchange_ratings PASSED                                                                                                              [ 78%]
tests/test_ratings.py::TestGetRatings::test_hidden_ratings_not_returned PASSED                                                                                                       [ 79%]
tests/test_ratings.py::TestRatingLabels::test_get_rating_labels PASSED                                                                                                               [ 79%]
tests/test_ratings.py::TestRatingAuthorization::test_unauthenticated_cannot_create_rating PASSED                                                                                     [ 80%]
tests/test_ratings.py::TestRatingAuthorization::test_non_participant_cannot_rate PASSED                                                                                              [ 80%]
tests/test_rbac.py::test_regular_user_access PASSED                                                                                                                                  [ 81%]
tests/test_rbac.py::test_regular_user_forbidden_moderator PASSED                                                                                                                     [ 81%]
tests/test_rbac.py::test_regular_user_forbidden_admin PASSED                                                                                                                         [ 82%]
tests/test_rbac.py::test_moderator_access_user_endpoint PASSED                                                                                                                       [ 82%]
tests/test_rbac.py::test_moderator_access_moderator_endpoint PASSED                                                                                                                  [ 82%]
tests/test_rbac.py::test_moderator_forbidden_admin PASSED                                                                                                                            [ 83%]
tests/test_rbac.py::test_admin_access_all_endpoints PASSED                                                                                                                           [ 83%]
tests/test_rbac.py::test_custom_role_dependency PASSED                                                                                                                               [ 84%]
tests/test_rbac.py::test_no_token_returns_401 PASSED                                                                                                                                 [ 84%]
tests/test_rbac.py::test_invalid_token_returns_401 PASSED                                                                                                                            [ 85%]
tests/test_rbac.py::test_inactive_user_denied PASSED                                                                                                                                 [ 85%]
tests/test_search.py::test_search_empty_database PASSED                                                                                                                              [ 86%]
tests/test_search.py::test_search_text_query PASSED                                                                                                                                  [ 86%]
tests/test_search.py::test_search_by_type_offer PASSED                                                                                                                               [ 87%]
tests/test_search.py::test_search_by_type_need PASSED                                                                                                                                [ 87%]
tests/test_search.py::test_search_by_tags_any PASSED                                                                                                                                 [ 88%]
tests/test_search.py::test_search_by_tags_all PASSED                                                                                                                                 [ 88%]
tests/test_search.py::test_search_by_remote_flag PASSED                                                                                                                              [ 88%]
tests/test_search.py::test_search_sort_by_recency PASSED                                                                                                                             [ 89%]
tests/test_search.py::test_search_pagination PASSED                                                                                                                                  [ 89%]
tests/test_search.py::test_search_combined_filters PASSED                                                                                                                            [ 90%]
tests/test_search.py::test_list_tags PASSED                                                                                                                                          [ 90%]
tests/test_search.py::test_tag_autocomplete PASSED                                                                                                                                   [ 91%]
tests/test_search.py::test_tags_created_on_demand PASSED                                                                                                                             [ 91%]
tests/test_social_media.py::TestSocialMediaUpdate::test_update_social_media_all_fields PASSED                                                                                        [ 92%]
tests/test_social_media.py::TestSocialMediaUpdate::test_update_social_media_partial PASSED                                                                                           [ 92%]
tests/test_social_media.py::TestSocialMediaUpdate::test_update_social_media_clear_existing PASSED                                                                                    [ 93%]
tests/test_social_media.py::TestSocialMediaUpdate::test_update_social_media_with_other_fields PASSED                                                                                 [ 93%]
tests/test_social_media.py::TestSocialMediaGet::test_get_own_profile_with_social_media PASSED                                                                                        [ 94%]
tests/test_social_media.py::TestSocialMediaGet::test_get_own_profile_without_social_media PASSED                                                                                     [ 94%]
tests/test_social_media.py::TestSocialMediaGet::test_get_other_user_profile_with_social_media PASSED                                                                                 [ 94%]
tests/test_social_media.py::TestSocialMediaGet::test_get_other_user_profile_without_social_media PASSED                                                                              [ 95%]
tests/test_social_media.py::TestSocialMediaGet::test_get_profile_public_no_auth PASSED                                                                                               [ 95%]
tests/test_social_media.py::TestSocialMediaValidation::test_social_blog_accepts_url PASSED                                                                                             [ 96%]
tests/test_social_media.py::TestSocialMediaValidation::test_social_username_accepts_simple_string PASSED                                                                               [ 96%]
tests/test_time_slots.py::test_create_offer_with_time_slots PASSED                                                                                                                   [ 97%]
tests/test_time_slots.py::test_create_offer_without_time_slots PASSED                                                                                                                [ 97%]
tests/test_time_slots.py::test_update_offer_time_slots PASSED                                                                                                                        [ 98%]
tests/test_time_slots.py::test_create_need_with_time_slots PASSED                                                                                                                    [ 98%]
tests/test_time_slots.py::test_invalid_time_range PASSED                                                                                                                             [ 99%]
tests/test_time_slots.py::test_invalid_time_format PASSED                                                                                                                            [ 99%]
tests/test_time_slots.py::test_invalid_date_format PASSED                                                                                                                            [100%]

===================================================================================== warnings summary =====================================================================================
../usr/local/lib/python3.11/site-packages/starlette/routing.py:712
  /usr/local/lib/python3.11/site-packages/starlette/routing.py:712: PytestCollectionWarning: cannot collect 'test_router' because it is not a function.
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

tests/test_notifications.py::test_notify_application_received
  /app/tests/test_notifications.py:386: DeprecationWarning:
          [WARNING] You probably want to use `session.exec()` instead of `session.query()`.

          `session.exec()` is SQLModel's own short version with increased type
          annotations.

          Or otherwise you might want to use `session.execute()` instead of
          `session.query()`.

    notifications = session.query(Notification).filter(

tests/test_notifications.py::test_notify_application_accepted
  /app/tests/test_notifications.py:422: DeprecationWarning:
          [WARNING] You probably want to use `session.query()` instead of `session.query()`.

          `session.exec()` is SQLModel's own short version with increased type
          annotations.

          Or otherwise you might want to use `session.execute()` instead of
          `session.query()`.

    notifications = session.query(Notification).filter(

tests/test_notifications.py::test_notify_exchange_completed
  /app/tests/test_notifications.py:469: DeprecationWarning:
          [WARNING] You probably want to use `session.exec()` instead of `session.query()`.

          `session.exec()` is SQLModel's own short version with increased type
          annotations.

          Or otherwise you might want to use `session.execute()` instead of
          `session.query()`.

    alice_notifications = session.query(Notification).filter(

tests/test_notifications.py::test_notify_exchange_completed
  /app/tests/test_notifications.py:475: DeprecationWarning:
          [WARNING] You probably want to use `session.exec()` instead of `session.query()`.

          `session.exec()` is SQLModel's own short version with increased type
          annotations.

          Or otherwise you might want to use `session.execute()` instead of
          `session.query()`.

    bob_notifications = session.query(Notification).filter(

tests/test_notifications.py::test_notify_exchange_awaiting_confirmation
  /app/tests/test_notifications.py:513: DeprecationWarning:
          [WARNING] You probably want to use `session.exec()` instead of `session.query()`.

          `session.exec()` is SQLModel's own short version with increased type
          annotations.

          Or otherwise you might want to use `session.execute()` instead of
          `session.query()`.

    notifications = session.query(Notification).filter(

tests/test_notifications.py::test_notify_rating_received
  /app/tests/test_notifications.py:537: DeprecationWarning:
          [WARNING] You probably want to use `session.exec()` instead of `session.query()`.

          `session.exec()` is SQLModel's own short version with increased type
          annotations.

          Or otherwise you might want to use `session.execute()` instead of
          `session.query()`.

    notifications = session.query(Notification).filter(

tests/test_notifications.py::test_notification_types
  /app/tests/test_notifications.py:594: DeprecationWarning:
          [WARNING] You probably want to use `session.exec()` instead of `session.query()`.

          `session.exec()` is SQLModel's own short version with increased type
          annotations.

          Or otherwise you might want to use `session.execute()` instead of
          `session.query()`.

    notifications = session.query(Notification).filter(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================================================== 216 passed, 1 skipped, 8 warnings in 70.39s (0:01:10) ===================================================================
```

# Project Plan

## Tech Stack

-   **Backend**: FastAPI, SQLModel, PostgreSQL, JWT auth, pytest
-   **Frontend**: React 18, TypeScript, Vite, Material-UI, TanStack
    Query, Leaflet maps
-   **Infrastructure**: Docker Compose, nginx

## Phase 1: Foundation

1.  **Project Setup**
    -   Initialize monorepo structure (`app/`, `frontend/`, `tests/`,
        `scripts/`, `infra/`)
    -   Set up Docker Compose with PostgreSQL, backend, frontend
        services
    -   Configure dependencies (pyproject.toml, package.json)
2.  **Database & Core Models**
    -   Design database schema (Users, Offers, Needs, Participants,
        Ledger, Tags)
    -   Implement SQLModel models with validation
    -   Set up Alembic migrations
    -   Create database initialization script
3.  **Authentication System**
    -   JWT authentication with role-based access (User/Moderator/Admin)
    -   User registration/login endpoints
    -   Password hashing with bcrypt
    -   Protected route middleware

## Phase 2: Core Features

4.  **Offers & Needs**
    -   CRUD endpoints for Offers and Needs
    -   Capacity management
    -   Location support (remote/in-person with coordinates)
    -   Time slot availability system
5.  **Tag System**
    -   Tag creation and management
    -   Semantic hierarchy (parent-child relationships)
    -   Tag synonyms and aliases
    -   Search by tags
6.  **Handshake Workflow**
    -   Participant model (PENDING -\> ACCEPTED -\> COMPLETED)
    -   Proposal/acceptance endpoints
    -   Status transitions with validation

## Phase 3: TimeBank & Ledger

7.  **TimeBank Ledger**
    -   Double-entry bookkeeping implementation
    -   Balance calculation (start: 5h, limit: -10h)
    -   Transaction types (EXCHANGE, TRANSFER, ADJUSTMENT, PENALTY)
    -   Ledger entry creation on handshake completion
8.  **User Balance Management**
    -   Real-time balance tracking
    -   Transaction history
    -   Reciprocity limit enforcement

## Phase 4: Frontend Core

9.  **Frontend Setup**
    -   React + TypeScript + Vite configuration
    -   Material-UI theme setup
    -   React Router navigation
    -   TanStack Query for API calls
    -   Auth context provider
10. **Key Pages**
    -   Landing page / Home
    -   Login/Register
    -   Offers list & detail
    -   Needs list & detail
    -   User profile
    -   Map view (Leaflet integration)

## Phase 5: Advanced Features

11. **Community Features**
    -   Forum (Discussions & Events)
    -   Comments and replies
    -   Rating system
    -   Badge system
12. **Moderation**
    -   Comment moderation endpoints
    -   Reporting system
    -   Moderator dashboard
    -   Penalty system
13. **Search & Discovery**
    -   Search by tags, location, keywords
    -   Map-based browsing
    -   Filtering and sorting

## Phase 6: Testing & Polish

14. **Testing**
    -   Backend pytest suite (auth, offers, needs, handshake, ledger,
        moderation)
    -   Golden path tests
15. **Documentation & Deployment**
    -   API documentation (FastAPI auto-docs)
    -   README with setup instructions
    -   Database seeding scripts
    -   Environment configuration

# Credit & Licenses

This project utilizes the following open-source libraries and
frameworks:

## Backend Dependencies

-   **FastAPI** - Modern, fast web framework for building APIs
    -   License: [MIT
        License](https://github.com/tiangolo/fastapi/blob/master/LICENSE)
    -   Source: https://github.com/tiangolo/fastapi
-   **SQLModel** - SQL databases in Python, designed for simplicity,
    compatibility, and robustness
    -   License: [MIT
        License](https://github.com/tiangolo/sqlmodel/blob/main/LICENSE)
    -   Source: https://github.com/tiangolo/sqlmodel
-   **Uvicorn** - Lightning-fast ASGI server
    -   License: [BSD
        License](https://github.com/encode/uvicorn/blob/master/LICENSE.md)
    -   Source: https://github.com/encode/uvicorn
-   **PostgreSQL** - Advanced open-source relational database
    -   License: [PostgreSQL
        License](https://www.postgresql.org/about/licence/)
    -   Source: https://www.postgresql.org/
-   **Pydantic** - Data validation using Python type annotations
    -   License: [MIT
        License](https://github.com/pydantic/pydantic/blob/main/LICENSE)
    -   Source: https://github.com/pydantic/pydantic
-   **Alembic** - Database migration tool for SQLAlchemy
    -   License: [MIT
        License](https://github.com/sqlalchemy/alembic/blob/main/LICENSE)
    -   Source: https://github.com/sqlalchemy/alembic
-   **psycopg** - PostgreSQL adapter for Python
    -   License:
        [LGPL-3.0](https://github.com/psycopg/psycopg/blob/master/LICENSE.txt)
    -   Source: https://github.com/psycopg/psycopg
-   **PyJWT** - JSON Web Token implementation in Python
    -   License: [MIT
        License](https://github.com/jpadilla/pyjwt/blob/master/LICENSE)
    -   Source: https://github.com/jpadilla/pyjwt
-   **bcrypt** - Modern password hashing for Python
    -   License: [Apache License
        2.0](https://github.com/pyca/bcrypt/blob/main/LICENSE)
    -   Source: https://github.com/pyca/bcrypt
-   **pytest** - Testing framework for Python
    -   License: [MIT
        License](https://github.com/pytest-dev/pytest/blob/main/LICENSE)
    -   Source: https://github.com/pytest-dev/pytest
-   **Black** - Python code formatter
    -   License: [MIT
        License](https://github.com/psf/black/blob/main/LICENSE)
    -   Source: https://github.com/psf/black
-   **Ruff** - Fast Python linter and code formatter
    -   License: [MIT
        License](https://github.com/astral-sh/ruff/blob/main/LICENSE)
    -   Source: https://github.com/astral-sh/ruff

## Frontend Dependencies

-   **React** - JavaScript library for building user interfaces
    -   License: [MIT
        License](https://github.com/facebook/react/blob/main/LICENSE)
    -   Source: https://github.com/facebook/react
-   **TypeScript** - Typed superset of JavaScript
    -   License: [Apache License
        2.0](https://github.com/microsoft/TypeScript/blob/main/LICENSE.txt)
    -   Source: https://github.com/microsoft/TypeScript
-   **Vite** - Next generation frontend tooling
    -   License: [MIT
        License](https://github.com/vitejs/vite/blob/main/LICENSE)
    -   Source: https://github.com/vitejs/vite
-   **Material-UI (MUI)** - React component library implementing
    Material Design
    -   License: [MIT
        License](https://github.com/mui/material-ui/blob/master/LICENSE)
    -   Source: https://github.com/mui/material-ui
-   **TanStack Query** - Powerful data synchronization for React
    -   License: [MIT
        License](https://github.com/TanStack/query/blob/main/LICENSE)
    -   Source: https://github.com/TanStack/query
-   **React Router** - Declarative routing for React
    -   License: [MIT
        License](https://github.com/remix-run/react-router/blob/main/LICENSE)
    -   Source: https://github.com/remix-run/react-router
-   **Leaflet** - Open-source JavaScript library for mobile-friendly
    interactive maps
    -   License: [BSD 2-Clause
        License](https://github.com/Leaflet/Leaflet/blob/main/LICENSE)
    -   Source: https://github.com/Leaflet/Leaflet
-   **React Leaflet** - React components for Leaflet maps
    -   License: [Hippocratic License
        2.1](https://github.com/PaulLeCam/react-leaflet/blob/master/LICENSE)
    -   Source: https://github.com/PaulLeCam/react-leaflet
-   **Axios** - Promise-based HTTP client
    -   License: [MIT
        License](https://github.com/axios/axios/blob/v1.x/LICENSE)
    -   Source: https://github.com/axios/axios
-   **date-fns** - Modern JavaScript date utility library
    -   License: [MIT
        License](https://github.com/date-fns/date-fns/blob/main/LICENSE.md)
    -   Source: https://github.com/date-fns/date-fns

## Development Tools

-   **Docker** - Platform for developing, shipping, and running
    applications
    -   License: [Apache License
        2.0](https://github.com/docker/docker/blob/master/LICENSE)
    -   Source: https://github.com/docker/docker
-   **Docker Compose** - Tool for defining and running multi-container
    Docker applications
    -   License: [Apache License
        2.0](https://github.com/docker/compose/blob/main/LICENSE)
    -   Source: https://github.com/docker/compose
-   **ESLint** - Pluggable JavaScript linter
    -   License: [MIT
        License](https://github.com/eslint/eslint/blob/main/LICENSE)
    -   Source: https://github.com/eslint/eslint

# Wiki Deliverables Link

https://github.com/Yusufss4/swe573-practice/wiki
