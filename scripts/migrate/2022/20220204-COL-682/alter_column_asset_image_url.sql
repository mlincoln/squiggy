BEGIN;

ALTER TABLE assets ALTER COLUMN download_url TYPE TEXT;
ALTER TABLE assets ALTER COLUMN image_url TYPE TEXT;
ALTER TABLE assets ALTER COLUMN pdf_url TYPE TEXT;
ALTER TABLE assets ALTER COLUMN thumbnail_url TYPE TEXT;
ALTER TABLE assets ALTER COLUMN url TYPE TEXT;

COMMIT;