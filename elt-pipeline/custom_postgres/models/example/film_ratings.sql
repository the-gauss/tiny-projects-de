WITH film_with_ratings AS (
    SELECT 
        film_id,
        title,
        release_date,
        price,
        rating,
        user_rating,
        CASE
            WHEN user_rating >= 4 THEN 'Excellent'  
            WHEN user_rating >= 3 THEN 'Good'
            WHEN user_rating >= 2 THEN 'Average'
            WHEN user_rating >= 1 THEN 'Poor'
            ELSE 'No Rating'
        END as rating_category
    FROM {{ ref('films') }}
),

actor_stats AS (
    SELECT
        fa.film_id,
        COUNT(DISTINCT fa.actor_id) AS actor_count
    FROM {{ ref('film_actors') }} fa
    GROUP BY fa.film_id
),

actor_film_ratings AS (
    SELECT
        fa1.film_id,
        AVG(f2.user_rating) AS avg_actor_rating
    FROM {{ ref('film_actors') }} fa1
    JOIN {{ ref('film_actors') }} fa2 ON fa1.actor_id = fa2.actor_id
    JOIN {{ ref('films') }} f2 ON fa2.film_id = f2.film_id
    GROUP BY fa1.film_id
),

films_with_actors AS (
    SELECT
        f.film_id,
        f.title,
        STRING_AGG(a.actor_name, ', ') AS actors
    FROM {{ ref('films') }} f
    LEFT JOIN {{ ref('film_actors') }} fa ON f.film_id = fa.film_id
    LEFT JOIN {{ ref('actors') }} a ON fa.actor_id = a.actor_id
    GROUP BY f.film_id, f.title
)

SELECT
    fwr.film_id,
    fwr.title,
    fwr.release_date,
    fwr.price,
    fwr.rating,
    fwr.user_rating,
    ast.actor_count,
    afr.avg_actor_rating,
    fwa.actors,
    fwr.rating_category
FROM film_with_ratings fwr
LEFT JOIN actor_stats ast ON fwr.film_id = ast.film_id
LEFT JOIN actor_film_ratings afr ON fwr.film_id = afr.film_id
LEFT JOIN films_with_actors fwa ON fwr.film_id = fwa.film_id;
