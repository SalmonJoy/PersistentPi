CREATE TABLE m08_campaigns(
 id TEXT PRIMARY KEY REFERENCES experiments(id), phase TEXT NOT NULL,
 preregistration_hash TEXT NOT NULL, freeze_hash TEXT, suite_hash TEXT NOT NULL,
 schedule_hash TEXT NOT NULL REFERENCES artifacts(hash), tier TEXT,
 state TEXT NOT NULL CHECK(state IN ('running','sealed','incomplete','scored')),
 created_utc TEXT NOT NULL, sealed_utc TEXT
);
CREATE TABLE m08_windows(
 run_id TEXT PRIMARY KEY REFERENCES runs(id), campaign_id TEXT NOT NULL REFERENCES m08_campaigns(id),
 task_id TEXT NOT NULL, arm TEXT NOT NULL CHECK(arm IN ('I','D','O','R')),
 candidate_index INTEGER NOT NULL CHECK(candidate_index BETWEEN 1 AND 5),
 parent_prefix TEXT REFERENCES m08_initial_prefixes(id), state_artifact TEXT REFERENCES artifacts(hash),
 UNIQUE(campaign_id,task_id,arm,candidate_index)
);
CREATE TABLE m08_initial_prefixes(
 id TEXT PRIMARY KEY REFERENCES artifacts(hash), campaign_id TEXT NOT NULL REFERENCES m08_campaigns(id),
 task_id TEXT NOT NULL, task_hash TEXT NOT NULL, manifest_hash TEXT NOT NULL REFERENCES manifests(hash),
 acquisition_run TEXT NOT NULL UNIQUE REFERENCES m08_windows(run_id),
 original_checkpoint TEXT NOT NULL REFERENCES artifacts(hash), candidate_checkpoint TEXT REFERENCES artifacts(hash),
 transcript_hash TEXT NOT NULL REFERENCES artifacts(hash), public_result_hash TEXT REFERENCES artifacts(hash),
 state_artifact TEXT NOT NULL REFERENCES artifacts(hash), created_utc TEXT NOT NULL,
 UNIQUE(campaign_id,task_id)
);
CREATE TRIGGER m08_prefix_no_update BEFORE UPDATE ON m08_initial_prefixes
BEGIN SELECT RAISE(ABORT,'InitialPrefix is immutable'); END;
CREATE TRIGGER m08_prefix_no_delete BEFORE DELETE ON m08_initial_prefixes
BEGIN SELECT RAISE(ABORT,'InitialPrefix is immutable'); END;
CREATE TRIGGER m08_window_parent BEFORE INSERT ON m08_windows
WHEN NEW.arm != 'I' AND NOT EXISTS(SELECT 1 FROM m08_initial_prefixes p
 WHERE p.id=NEW.parent_prefix AND p.campaign_id=NEW.campaign_id AND p.task_id=NEW.task_id)
BEGIN SELECT RAISE(ABORT,'Window must descend from the exact task prefix'); END;
CREATE TRIGGER m08_window_identity BEFORE UPDATE OF run_id,campaign_id,task_id,arm,candidate_index,parent_prefix ON m08_windows
BEGIN SELECT RAISE(ABORT,'Window lineage is immutable'); END;
CREATE TRIGGER m08_window_state_once BEFORE UPDATE OF state_artifact ON m08_windows
WHEN OLD.state_artifact IS NOT NULL
BEGIN SELECT RAISE(ABORT,'Completed window state is immutable'); END;
CREATE TABLE m08_branches(
 id TEXT PRIMARY KEY, prefix_id TEXT NOT NULL REFERENCES m08_initial_prefixes(id),
 arm TEXT NOT NULL CHECK(arm IN ('D','O','R')), lineage_hash TEXT NOT NULL REFERENCES artifacts(hash),
 UNIQUE(prefix_id,arm)
);
CREATE TRIGGER m08_branch_no_update BEFORE UPDATE ON m08_branches
BEGIN SELECT RAISE(ABORT,'Branch lineage is immutable'); END;
CREATE TRIGGER m08_branch_no_delete BEFORE DELETE ON m08_branches
BEGIN SELECT RAISE(ABORT,'Branch lineage is immutable'); END;
CREATE TABLE m08_receipts(
 id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES m08_windows(run_id),
 kind TEXT NOT NULL CHECK(kind IN ('model','tool','window')),
 payload_hash TEXT NOT NULL REFERENCES artifacts(hash)
);
CREATE TRIGGER m08_receipt_no_update BEFORE UPDATE ON m08_receipts
BEGIN SELECT RAISE(ABORT,'Physical receipt is immutable'); END;
CREATE TRIGGER m08_receipt_no_delete BEFORE DELETE ON m08_receipts
BEGIN SELECT RAISE(ABORT,'Physical receipt is immutable'); END;
CREATE TABLE m08_scores(
 campaign_id TEXT NOT NULL REFERENCES m08_campaigns(id), task_id TEXT NOT NULL,
 checkpoint_hash TEXT NOT NULL REFERENCES artifacts(hash), outcome TEXT NOT NULL,
 result_hash TEXT NOT NULL REFERENCES artifacts(hash), PRIMARY KEY(campaign_id,task_id,checkpoint_hash)
);
CREATE TRIGGER m08_hidden_after_seal BEFORE INSERT ON evaluations
WHEN NEW.split='hidden' AND (SELECT protocol_version FROM runs WHERE id=NEW.run_id)='0.5'
 AND NOT EXISTS(SELECT 1 FROM m08_windows w JOIN m08_campaigns c ON w.campaign_id=c.id
                WHERE w.run_id=NEW.run_id AND c.state IN ('sealed','scored'))
BEGIN SELECT RAISE(ABORT,'M0.8 hidden scoring requires sealed generation'); END;
CREATE TRIGGER m08_score_after_seal BEFORE INSERT ON m08_scores
WHEN (SELECT state FROM m08_campaigns WHERE id=NEW.campaign_id) NOT IN ('sealed','scored')
BEGIN SELECT RAISE(ABORT,'M0.8 scores require sealed generation'); END;
CREATE TABLE m08_retired_cohorts(suite_hash TEXT PRIMARY KEY, campaign_id TEXT NOT NULL REFERENCES m08_campaigns(id), retired_utc TEXT NOT NULL);
CREATE TABLE m08_overhead(
 id TEXT PRIMARY KEY, campaign_id TEXT NOT NULL REFERENCES m08_campaigns(id),
 kind TEXT NOT NULL, payload_hash TEXT NOT NULL REFERENCES artifacts(hash)
);
