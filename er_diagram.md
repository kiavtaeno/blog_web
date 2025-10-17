# ER Diagram для блога


```mermaid
erDiagram
    users {
        bigint id PK
        varchar email UK
        varchar username UK
        varchar password_hash
        timestamp created_at
        timestamp updated_at
    }

    journeys {
        bigint id PK
        bigint traveler_id FK
        varchar destination
        text story
        varchar image_url
        decimal location_lat
        decimal location_lng
        varchar status
        int view_count
        int like_count
        timestamp created_at
        timestamp updated_at
    }

    categories {
        bigint id PK
        varchar name UK
        varchar slug UK
        text description
        timestamp created_at
    }

    journey_categories {
        bigint journey_id PK,FK
        bigint category_id PK,FK
        timestamp created_at
    }

    favorites {
        bigint id PK
        bigint user_id FK
        bigint journey_id FK
        timestamp created_at
    }

    comments {
        bigint id PK
        text content
        bigint author_id FK
        bigint journey_id FK
        bigint parent_comment_id FK
        timestamp created_at
        timestamp updated_at
    }

    subscriptions {
        bigint id PK
        bigint subscriber_id FK
        bigint target_user_id FK
        timestamp created_at
    }

    users ||--o{ journeys : "has many"
    users ||--o{ comments : "writes"
    users ||--o{ favorites : "creates"
    users ||--o{ subscriptions : "subscribes to"
    journeys ||--o{ comments : "has"
    journeys ||--o{ favorites : "favorited by"
    journeys }o--o{ categories : "tagged with"
    comments ||--o{ comments : "replies to"