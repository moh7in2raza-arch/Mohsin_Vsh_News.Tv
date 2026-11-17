--
-- PostgreSQL database dump
--

\restrict 5rgA9sDm8fODdrxXE8DyXqNPLoTmbHzLbRQheamXZ5GGtdLQawwbFBCXOL1AIYt

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: accounting; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA accounting;


ALTER SCHEMA accounting OWNER TO postgres;

--
-- Name: audit; Type: SCHEMA; Schema: -; Owner: erp_app
--

CREATE SCHEMA audit;


ALTER SCHEMA audit OWNER TO erp_app;

--
-- Name: hr; Type: SCHEMA; Schema: -; Owner: erp_app
--

CREATE SCHEMA hr;


ALTER SCHEMA hr OWNER TO erp_app;

--
-- Name: inventory; Type: SCHEMA; Schema: -; Owner: erp_app
--

CREATE SCHEMA inventory;


ALTER SCHEMA inventory OWNER TO erp_app;

--
-- Name: payroll; Type: SCHEMA; Schema: -; Owner: erp_app
--

CREATE SCHEMA payroll;


ALTER SCHEMA payroll OWNER TO erp_app;

--
-- PostgreSQL database dump complete
--

\unrestrict 5rgA9sDm8fODdrxXE8DyXqNPLoTmbHzLbRQheamXZ5GGtdLQawwbFBCXOL1AIYt

