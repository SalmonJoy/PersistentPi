CREATE TABLE manifests(hash TEXT PRIMARY KEY, kind TEXT NOT NULL, schema_version INTEGER NOT NULL, json TEXT NOT NULL);
CREATE TABLE experiments(id TEXT PRIMARY KEY, manifest_hash TEXT NOT NULL REFERENCES manifests(hash), protocol_version TEXT NOT NULL, created_utc TEXT NOT NULL);
CREATE TABLE artifacts(hash TEXT PRIMARY KEY, kind TEXT NOT NULL, relative_path TEXT NOT NULL, bytes INTEGER NOT NULL, visibility TEXT NOT NULL);
CREATE TABLE runs(
 id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL REFERENCES experiments(id), trial_key TEXT NOT NULL,
 mode TEXT NOT NULL CHECK(mode IN ('development','formal')), task_id TEXT NOT NULL, task_hash TEXT NOT NULL,
 fixture_version TEXT NOT NULL, protocol_version TEXT NOT NULL, scaffold_id TEXT NOT NULL,
 scaffold_hash TEXT NOT NULL, parent_scaffold_id TEXT, scaffold_version TEXT NOT NULL,
 seed INTEGER NOT NULL, replicate INTEGER NOT NULL, manifest_hash TEXT NOT NULL REFERENCES manifests(hash),
 git_commit TEXT, dirty INTEGER NOT NULL, status TEXT NOT NULL, stop_reason TEXT,
 budget_json TEXT NOT NULL, usage_json TEXT NOT NULL, platform_json TEXT NOT NULL,
 owner_pid INTEGER NOT NULL, owner_identity TEXT, stop_requested INTEGER NOT NULL DEFAULT 0,
 initial_checkpoint TEXT REFERENCES artifacts(hash), selected_checkpoint TEXT REFERENCES artifacts(hash),
 benchmark_score REAL, evaluation_status TEXT NOT NULL DEFAULT 'pending', created_utc TEXT NOT NULL, ended_utc TEXT
);
CREATE UNIQUE INDEX formal_trial_key ON runs(trial_key) WHERE mode='formal';
CREATE TABLE attempts(
 id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), ordinal INTEGER NOT NULL,
 checkpoint_hash TEXT NOT NULL REFERENCES artifacts(hash), parent_checkpoint_hash TEXT REFERENCES artifacts(hash),
 outcome TEXT NOT NULL, result_json TEXT, UNIQUE(run_id,ordinal)
);
CREATE TABLE evaluations(
 id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), attempt_id TEXT REFERENCES attempts(id),
 checkpoint_hash TEXT NOT NULL REFERENCES artifacts(hash), evaluator_hash TEXT NOT NULL,
 split TEXT NOT NULL CHECK(split IN ('public','hidden')), outcome TEXT NOT NULL, score REAL,
 result_json TEXT NOT NULL
);
CREATE TRIGGER hidden_after_runner BEFORE INSERT ON evaluations
WHEN NEW.split='hidden' AND (SELECT status FROM runs WHERE id=NEW.run_id) != 'finished'
BEGIN SELECT RAISE(ABORT,'Hidden evaluation requires a terminated Runner'); END;
CREATE TABLE events(
 id INTEGER PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), sequence INTEGER NOT NULL,
 utc TEXT NOT NULL, monotonic REAL NOT NULL, session_id TEXT NOT NULL, actor TEXT NOT NULL,
 type TEXT NOT NULL, payload_version INTEGER NOT NULL, payload_json TEXT NOT NULL,
 UNIQUE(run_id,sequence)
);
CREATE INDEX events_run_sequence ON events(run_id,sequence);
