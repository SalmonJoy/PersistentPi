CREATE TABLE m09_campaigns(
 id TEXT PRIMARY KEY REFERENCES experiments(id), protocol TEXT NOT NULL CHECK(protocol='0.6'),
 phase TEXT NOT NULL CHECK(phase IN ('references','search','qualification','finished','stopped')),
 config_hash TEXT NOT NULL REFERENCES manifests(hash), state_json TEXT NOT NULL, created_utc TEXT NOT NULL
);
CREATE TABLE m09_cohorts(
 campaign TEXT NOT NULL REFERENCES m09_campaigns(id), name TEXT NOT NULL CHECK(name IN ('search','qualification')),
 hash TEXT NOT NULL, manifest_hash TEXT NOT NULL REFERENCES artifacts(hash),
 PRIMARY KEY(campaign,name), UNIQUE(campaign,hash)
);
CREATE TABLE m09_members(
 campaign TEXT NOT NULL, cohort_hash TEXT NOT NULL, task_id TEXT NOT NULL, task_hash TEXT NOT NULL,
 family TEXT NOT NULL, template TEXT NOT NULL, subset TEXT NOT NULL CHECK(subset IN ('screen','remaining','qualification')),
 PRIMARY KEY(campaign,cohort_hash,task_id), FOREIGN KEY(campaign,cohort_hash) REFERENCES m09_cohorts(campaign,hash)
);
CREATE TABLE m09_scaffolds(
 id TEXT PRIMARY KEY, specification TEXT NOT NULL REFERENCES artifacts(hash), compiler TEXT NOT NULL,
 renderer TEXT NOT NULL, catalog_hash TEXT NOT NULL REFERENCES artifacts(hash), protocol TEXT NOT NULL CHECK(protocol='0.6')
);
CREATE TABLE m09_operations(
 id TEXT PRIMARY KEY, campaign TEXT NOT NULL REFERENCES m09_campaigns(id),
 kind TEXT NOT NULL CHECK(kind IN ('planner','runner')), state TEXT NOT NULL CHECK(state IN ('reserved','started','completed','indeterminate')),
 reservation_json TEXT NOT NULL, usage_json TEXT, created_utc TEXT NOT NULL, started_utc TEXT, ended_utc TEXT
);
CREATE TABLE m09_disclosures(
 id TEXT PRIMARY KEY REFERENCES artifacts(hash), campaign TEXT NOT NULL REFERENCES m09_campaigns(id),
 policy TEXT NOT NULL, observation_hash TEXT NOT NULL REFERENCES artifacts(hash), created_utc TEXT NOT NULL
);
CREATE TABLE m09_planner_requests(
 id TEXT PRIMARY KEY REFERENCES m09_operations(id), campaign TEXT NOT NULL REFERENCES m09_campaigns(id),
 round INTEGER NOT NULL CHECK(round BETWEEN 1 AND 4), slot INTEGER NOT NULL CHECK(slot IN (1,2)),
 disclosure_id TEXT NOT NULL REFERENCES m09_disclosures(id), request_hash TEXT NOT NULL REFERENCES artifacts(hash),
 configuration_hash TEXT NOT NULL REFERENCES artifacts(hash), UNIQUE(campaign,round,slot)
);
CREATE TABLE m09_planner_responses(
 request_id TEXT PRIMARY KEY REFERENCES m09_planner_requests(id), response_hash TEXT NOT NULL REFERENCES artifacts(hash),
 identity_hash TEXT NOT NULL REFERENCES artifacts(hash), usage_hash TEXT NOT NULL REFERENCES artifacts(hash),
 created_utc TEXT NOT NULL, latency REAL NOT NULL CHECK(latency>=0)
);
CREATE TABLE m09_proposals(
 id TEXT PRIMARY KEY, campaign TEXT NOT NULL REFERENCES m09_campaigns(id), request_id TEXT NOT NULL UNIQUE REFERENCES m09_planner_requests(id),
 scaffold_id TEXT REFERENCES m09_scaffolds(id), envelope_hash TEXT NOT NULL REFERENCES artifacts(hash),
 validation TEXT NOT NULL CHECK(validation IN ('valid','invalid','duplicate')), reason TEXT NOT NULL,
 resource_hash TEXT NOT NULL REFERENCES artifacts(hash), created_utc TEXT NOT NULL
);
CREATE TABLE m09_parents(
 proposal_id TEXT NOT NULL REFERENCES m09_proposals(id), scaffold_id TEXT NOT NULL REFERENCES m09_scaffolds(id),
 PRIMARY KEY(proposal_id,scaffold_id)
);
CREATE TABLE m09_validations(
 id TEXT PRIMARY KEY REFERENCES artifacts(hash), proposal_id TEXT NOT NULL REFERENCES m09_proposals(id),
 state TEXT NOT NULL, reason TEXT NOT NULL, created_utc TEXT NOT NULL
);
CREATE TABLE m09_jobs(
 id TEXT PRIMARY KEY REFERENCES m09_operations(id), campaign TEXT NOT NULL REFERENCES m09_campaigns(id),
 scaffold_id TEXT NOT NULL REFERENCES m09_scaffolds(id), cohort_hash TEXT NOT NULL, task_id TEXT NOT NULL,
 stage TEXT NOT NULL CHECK(stage IN ('reference','screen','remaining','qualification')),
 result_hash TEXT REFERENCES artifacts(hash), run_id TEXT REFERENCES runs(id),
 UNIQUE(campaign,scaffold_id,cohort_hash,task_id),
 FOREIGN KEY(campaign,cohort_hash,task_id) REFERENCES m09_members(campaign,cohort_hash,task_id)
);
CREATE TABLE m09_archive(
 campaign TEXT NOT NULL REFERENCES m09_campaigns(id), scaffold_id TEXT NOT NULL REFERENCES m09_scaffolds(id),
 score_hash TEXT NOT NULL REFERENCES artifacts(hash), generated INTEGER NOT NULL CHECK(generated IN (0,1)),
 PRIMARY KEY(campaign,scaffold_id)
);
CREATE TABLE m09_decisions(
 id TEXT PRIMARY KEY REFERENCES artifacts(hash), campaign TEXT NOT NULL REFERENCES m09_campaigns(id),
 kind TEXT NOT NULL, created_utc TEXT NOT NULL
);
CREATE TABLE m09_finalists(
 campaign TEXT PRIMARY KEY REFERENCES m09_campaigns(id), scaffold_id TEXT NOT NULL,
 freeze_hash TEXT NOT NULL REFERENCES artifacts(hash), entry_passed INTEGER NOT NULL CHECK(entry_passed=1),
 FOREIGN KEY(campaign,scaffold_id) REFERENCES m09_archive(campaign,scaffold_id)
);
CREATE TABLE m09_phase_events(
 campaign TEXT NOT NULL REFERENCES m09_campaigns(id), sequence INTEGER NOT NULL, phase TEXT NOT NULL,
 state_hash TEXT NOT NULL REFERENCES artifacts(hash), created_utc TEXT NOT NULL, PRIMARY KEY(campaign,sequence)
);
CREATE TRIGGER m09_no_hidden BEFORE INSERT ON evaluations
WHEN NEW.split='hidden' AND (SELECT protocol_version FROM runs WHERE id=NEW.run_id)='0.6'
BEGIN SELECT RAISE(ABORT,'Protocol 0.6 hidden scoring is not authorized'); END;
CREATE TRIGGER m09_job_phase BEFORE INSERT ON m09_jobs
WHEN (NEW.stage='qualification' AND ((SELECT phase FROM m09_campaigns WHERE id=NEW.campaign)!='qualification'
 OR NOT EXISTS(SELECT 1 FROM m09_finalists WHERE campaign=NEW.campaign)))
 OR (NEW.stage!='qualification' AND (SELECT phase FROM m09_campaigns WHERE id=NEW.campaign) NOT IN ('references','search'))
BEGIN SELECT RAISE(ABORT,'Job phase barrier denied'); END;
CREATE TRIGGER m09_job_actor BEFORE INSERT ON m09_jobs
WHEN NOT EXISTS(SELECT 1 FROM m09_operations WHERE id=NEW.id AND campaign=NEW.campaign AND kind='runner')
 OR (NEW.stage='qualification' AND NOT EXISTS(SELECT 1 FROM m09_finalists WHERE campaign=NEW.campaign AND scaffold_id=NEW.scaffold_id)
 AND NOT EXISTS(SELECT 1 FROM m09_archive WHERE campaign=NEW.campaign AND scaffold_id=NEW.scaffold_id AND generated=0))
BEGIN SELECT RAISE(ABORT,'Job actor/qualification arm denied'); END;
CREATE TRIGGER m09_request_actor BEFORE INSERT ON m09_planner_requests
WHEN NOT EXISTS(SELECT 1 FROM m09_operations WHERE id=NEW.id AND campaign=NEW.campaign AND kind='planner')
 OR (SELECT phase FROM m09_campaigns WHERE id=NEW.campaign)!='search'
BEGIN SELECT RAISE(ABORT,'Planner request actor/phase denied'); END;
CREATE TRIGGER m09_job_subset BEFORE INSERT ON m09_jobs
WHEN (NEW.stage IN ('screen','remaining','qualification') AND NEW.stage!=(SELECT subset FROM m09_members
 WHERE campaign=NEW.campaign AND cohort_hash=NEW.cohort_hash AND task_id=NEW.task_id))
BEGIN SELECT RAISE(ABORT,'Job subset mismatch'); END;
CREATE TRIGGER m09_archive_complete BEFORE INSERT ON m09_archive
WHEN (SELECT COUNT(*) FROM m09_jobs j JOIN m09_operations o ON j.id=o.id
 JOIN m09_cohorts c ON j.campaign=c.campaign AND j.cohort_hash=c.hash
 WHERE j.campaign=NEW.campaign AND j.scaffold_id=NEW.scaffold_id AND c.name='search'
 AND o.state='completed' AND j.result_hash IS NOT NULL)!=32
BEGIN SELECT RAISE(ABORT,'Archive requires complete identical Search32'); END;
CREATE TRIGGER m09_finalist_closed BEFORE INSERT ON m09_finalists
WHEN (SELECT phase FROM m09_campaigns WHERE id=NEW.campaign)!='search'
 OR json_extract((SELECT state_json FROM m09_campaigns WHERE id=NEW.campaign),'$.round')!=5
 OR NOT EXISTS(SELECT 1 FROM m09_archive WHERE campaign=NEW.campaign AND scaffold_id=NEW.scaffold_id AND generated=1)
BEGIN SELECT RAISE(ABORT,'Finalist requires closed search and generated full entry'); END;
CREATE TRIGGER m09_operation_once BEFORE UPDATE ON m09_operations WHEN OLD.state IN ('completed','indeterminate')
BEGIN SELECT RAISE(ABORT,'Completed or indeterminate operation is immutable'); END;
CREATE TRIGGER m09_job_once BEFORE UPDATE ON m09_jobs WHEN OLD.result_hash IS NOT NULL
BEGIN SELECT RAISE(ABORT,'Completed job is immutable'); END;
CREATE TRIGGER m09_phase_forward BEFORE UPDATE OF phase ON m09_campaigns
WHEN OLD.phase IN ('finished','stopped') AND NEW.phase!=OLD.phase
BEGIN SELECT RAISE(ABORT,'Terminal campaign cannot resume'); END;
CREATE TRIGGER m09_scaffold_no_update BEFORE UPDATE ON m09_scaffolds BEGIN SELECT RAISE(ABORT,'Immutable scaffold'); END;
CREATE TRIGGER m09_scaffold_no_delete BEFORE DELETE ON m09_scaffolds BEGIN SELECT RAISE(ABORT,'Immutable scaffold'); END;
CREATE TRIGGER m09_cohort_no_update BEFORE UPDATE ON m09_cohorts BEGIN SELECT RAISE(ABORT,'Immutable cohort'); END;
CREATE TRIGGER m09_cohort_no_delete BEFORE DELETE ON m09_cohorts BEGIN SELECT RAISE(ABORT,'Immutable cohort'); END;
CREATE TRIGGER m09_member_no_update BEFORE UPDATE ON m09_members BEGIN SELECT RAISE(ABORT,'Immutable membership'); END;
CREATE TRIGGER m09_member_no_delete BEFORE DELETE ON m09_members BEGIN SELECT RAISE(ABORT,'Immutable membership'); END;
CREATE TRIGGER m09_proposal_no_update BEFORE UPDATE ON m09_proposals BEGIN SELECT RAISE(ABORT,'Immutable proposal'); END;
CREATE TRIGGER m09_proposal_no_delete BEFORE DELETE ON m09_proposals BEGIN SELECT RAISE(ABORT,'Immutable proposal'); END;
CREATE TRIGGER m09_parent_no_update BEFORE UPDATE ON m09_parents BEGIN SELECT RAISE(ABORT,'Immutable parent'); END;
CREATE TRIGGER m09_parent_no_delete BEFORE DELETE ON m09_parents BEGIN SELECT RAISE(ABORT,'Immutable parent'); END;
CREATE TRIGGER m09_disclosure_no_update BEFORE UPDATE ON m09_disclosures BEGIN SELECT RAISE(ABORT,'Immutable disclosure'); END;
CREATE TRIGGER m09_disclosure_no_delete BEFORE DELETE ON m09_disclosures BEGIN SELECT RAISE(ABORT,'Immutable disclosure'); END;
CREATE TRIGGER m09_request_no_update BEFORE UPDATE ON m09_planner_requests BEGIN SELECT RAISE(ABORT,'Immutable Planner request'); END;
CREATE TRIGGER m09_request_no_delete BEFORE DELETE ON m09_planner_requests BEGIN SELECT RAISE(ABORT,'Immutable Planner request'); END;
CREATE TRIGGER m09_response_no_update BEFORE UPDATE ON m09_planner_responses BEGIN SELECT RAISE(ABORT,'Immutable Planner response'); END;
CREATE TRIGGER m09_response_no_delete BEFORE DELETE ON m09_planner_responses BEGIN SELECT RAISE(ABORT,'Immutable Planner response'); END;
CREATE TRIGGER m09_validation_no_update BEFORE UPDATE ON m09_validations BEGIN SELECT RAISE(ABORT,'Immutable validation'); END;
CREATE TRIGGER m09_validation_no_delete BEFORE DELETE ON m09_validations BEGIN SELECT RAISE(ABORT,'Immutable validation'); END;
CREATE TRIGGER m09_archive_no_update BEFORE UPDATE ON m09_archive BEGIN SELECT RAISE(ABORT,'Immutable archive'); END;
CREATE TRIGGER m09_archive_no_delete BEFORE DELETE ON m09_archive BEGIN SELECT RAISE(ABORT,'Immutable archive'); END;
CREATE TRIGGER m09_finalist_no_update BEFORE UPDATE ON m09_finalists BEGIN SELECT RAISE(ABORT,'Immutable finalist'); END;
CREATE TRIGGER m09_finalist_no_delete BEFORE DELETE ON m09_finalists BEGIN SELECT RAISE(ABORT,'Immutable finalist'); END;
CREATE TRIGGER m09_decision_no_update BEFORE UPDATE ON m09_decisions BEGIN SELECT RAISE(ABORT,'Immutable decision'); END;
CREATE TRIGGER m09_decision_no_delete BEFORE DELETE ON m09_decisions BEGIN SELECT RAISE(ABORT,'Immutable decision'); END;
CREATE TRIGGER m09_phase_no_update BEFORE UPDATE ON m09_phase_events BEGIN SELECT RAISE(ABORT,'Immutable phase receipt'); END;
CREATE TRIGGER m09_phase_no_delete BEFORE DELETE ON m09_phase_events BEGIN SELECT RAISE(ABORT,'Immutable phase receipt'); END;
CREATE TRIGGER m09_job_identity BEFORE UPDATE OF id,campaign,scaffold_id,cohort_hash,task_id,stage ON m09_jobs BEGIN SELECT RAISE(ABORT,'Immutable job identity'); END;
CREATE TRIGGER m09_job_no_delete BEFORE DELETE ON m09_jobs BEGIN SELECT RAISE(ABORT,'Immutable job'); END;
CREATE TRIGGER m09_operation_identity BEFORE UPDATE OF id,campaign,kind,reservation_json,created_utc ON m09_operations BEGIN SELECT RAISE(ABORT,'Immutable operation identity'); END;
CREATE TRIGGER m09_operation_no_delete BEFORE DELETE ON m09_operations BEGIN SELECT RAISE(ABORT,'Immutable receipt'); END;
