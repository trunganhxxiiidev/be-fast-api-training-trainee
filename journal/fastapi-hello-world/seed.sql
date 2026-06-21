INSERT INTO users (email, name, role, created_at) VALUES
    ('ada@example.com', 'Ada Lovelace', 'admin', '2026-06-01 09:00:00+00'),
    ('linus@example.com', 'Linus Torvalds', 'member', '2026-06-01 10:00:00+00'),
    ('grace@example.com', 'Grace Hopper', 'member', '2026-06-01 11:00:00+00');

INSERT INTO posts (user_id, title, body, published, created_at) VALUES
    (1, 'FastAPI routers in practice', 'Thin handlers and clear routers.', TRUE, '2026-06-14 09:00:00+00'),
    (1, 'Pydantic response models', 'Separate input and output schemas.', TRUE, '2026-06-13 09:00:00+00'),
    (1, 'Service layer notes', 'Move business logic out of routes.', TRUE, '2026-06-12 09:00:00+00'),
    (2, 'PostgreSQL constraints', 'Let the database protect invariants.', TRUE, '2026-06-11 09:00:00+00'),
    (2, 'Index basics', 'Indexes speed reads but slow writes.', TRUE, '2026-06-10 09:00:00+00'),
    (2, 'Transaction basics', 'Commit related changes together.', FALSE, '2026-06-09 09:00:00+00'),
    (3, 'Normalization basics', 'Avoid duplicated drifting data.', TRUE, '2026-06-08 09:00:00+00'),
    (3, 'Many to many tags', 'Use a join table for tags.', TRUE, '2026-06-07 09:00:00+00'),
    (3, 'Old SQL note', 'This post is outside the seven day window.', TRUE, '2026-05-25 09:00:00+00'),
    (1, 'Draft API checklist', 'A draft post without comments.', FALSE, '2026-06-14 12:00:00+00');

INSERT INTO tags (name, created_at) VALUES
    ('python', '2026-06-01 12:00:00+00'),
    ('fastapi', '2026-06-01 12:01:00+00'),
    ('postgresql', '2026-06-01 12:02:00+00'),
    ('sql', '2026-06-01 12:03:00+00'),
    ('backend', '2026-06-01 12:04:00+00');

INSERT INTO post_tags (post_id, tag_id) VALUES
    (1, 1), (1, 2), (1, 5),
    (2, 1), (2, 2),
    (3, 2), (3, 5),
    (4, 3), (4, 4),
    (5, 3), (5, 4), (5, 5),
    (6, 3),
    (7, 3), (7, 4),
    (8, 3), (8, 4), (8, 5),
    (9, 4),
    (10, 2), (10, 5);

INSERT INTO comments (post_id, user_id, body, created_at) VALUES
    (1, 2, 'Clear router example.', '2026-06-14 10:00:00+00'),
    (1, 3, 'This helps a lot.', '2026-06-14 10:05:00+00'),
    (1, 1, 'I will add tests next.', '2026-06-14 10:10:00+00'),
    (1, 2, 'Nice structure.', '2026-06-14 10:15:00+00'),
    (1, 3, 'Good reminder about tags.', '2026-06-14 10:20:00+00'),
    (2, 2, 'Response models prevent leaks.', '2026-06-13 10:00:00+00'),
    (2, 3, 'Useful for docs too.', '2026-06-13 10:05:00+00'),
    (2, 1, 'Validation is clearer now.', '2026-06-13 10:10:00+00'),
    (2, 2, 'Nice one.', '2026-06-13 10:15:00+00'),
    (3, 2, 'Services make tests easier.', '2026-06-12 10:00:00+00'),
    (3, 3, 'Routes stay small.', '2026-06-12 10:05:00+00'),
    (3, 1, 'This will help Day 8.', '2026-06-12 10:10:00+00'),
    (4, 1, 'DB constraints are underrated.', '2026-06-11 10:00:00+00'),
    (4, 3, 'CHECK constraints are useful.', '2026-06-11 10:05:00+00'),
    (4, 2, 'Unique email belongs in DB too.', '2026-06-11 10:10:00+00'),
    (5, 1, 'Index order matters.', '2026-06-10 10:00:00+00'),
    (5, 3, 'Seq scan on tiny tables is fine.', '2026-06-10 10:05:00+00'),
    (6, 1, 'Transactions protect consistency.', '2026-06-09 10:00:00+00'),
    (6, 2, 'Rollback is useful while practicing.', '2026-06-09 10:05:00+00'),
    (7, 1, 'Normalization avoids drift.', '2026-06-08 10:00:00+00'),
    (7, 2, 'Do not store comma separated tags.', '2026-06-08 10:05:00+00'),
    (8, 1, 'Join tables are mechanical.', '2026-06-07 10:00:00+00'),
    (9, 1, 'Old comment one.', '2026-05-26 10:00:00+00'),
    (9, 2, 'Old comment two.', '2026-05-26 10:05:00+00'),
    (9, 3, 'Old comment three.', '2026-05-26 10:10:00+00');
