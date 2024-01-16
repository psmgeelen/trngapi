CREATE OR REPLACE PROCEDURE delete_byte_rows(job_id INT, config JSONB)
    LANGUAGE PLPGSQL AS
    $$
    BEGIN
        RAISE NOTICE 'DELETING in the job % with config%', job_id, config;
        WITH summary AS (
            select max(id) as max_id
            from public.random_bytes_inf
        )
        DELETE FROM public.random_bytes_inf USING summary
            WHERE public.random_bytes_inf.id < summary.max_id - 60000;
        COMMIT;
    END
    $$;