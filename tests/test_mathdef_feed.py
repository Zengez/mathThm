"""mathThm v2 feed consumer contract — offline regression tests."""
import hashlib
import json
import unittest
from scripts.build_site import validate_v2, verify_theorem_hints


def sample():
    snapshot={"schema":"mathdef.definition-snapshot.v2",
      "definitions":[{
         "id":"g.compact","term":"Compact space","original_ids":["topology.compactness"],
         "meanings":[{"id":"m.compact","subject":"Topology"}],
         "formulations":[{"key":"f.compact","meaning_id":"m.compact",
           "subject":"Topology","body":"Every open cover has finite subcover."}]
      }],
      "consolidated_ids":{"group_aliases":{"g.old":"g.compact"},
         "meaning_aliases":{"m.old":"m.compact"},
         "formulation_aliases":{"f.old":"f.compact"}}}
    raw=(json.dumps(snapshot,sort_keys=True)+"\n").encode()
    digest=hashlib.sha256(raw).hexdigest()
    manifest={"schema":"mathdef.definition-manifest.v2",
       "snapshot_schema":"mathdef.definition-snapshot.v2",
       "dataset":"merged","snapshot_path":"snapshot.json",
       "version":"sha256:"+digest,"sha256":digest,
       "definition_count":1,"meaning_count":1,"formulation_count":1,
       "original_definition_count":1}
    return manifest,raw

class FeedTests(unittest.TestCase):
    def test_v2_verification_and_historical_hints(self):
        manifest,raw=sample()
        data=validate_v2(manifest,raw)
        theorem={"records":[{"link_hints":[["compact","topology.compactness"],
                             ["compact","g.old"]]}]}
        self.assertEqual(verify_theorem_hints(data,theorem),2)

    def test_checksum_and_old_dataset_rejected(self):
        manifest,raw=sample()
        with self.assertRaisesRegex(ValueError,"checksum"):
            validate_v2(manifest,raw+b"corrupted")
        manifest=dict(manifest,dataset="production")
        with self.assertRaisesRegex(ValueError,"manifest"):
            validate_v2(manifest,raw)

    def test_unresolved_old_ids_block_incomplete_bundle(self):
        manifest,raw=sample()
        data=validate_v2(manifest,raw)
        with self.assertRaisesRegex(ValueError,"lost theorem link hint"):
            verify_theorem_hints(data,{"records":[{"link_hints":[["term","lost.id"]]}]})

    def test_missing_context_and_missing_redirect_registry_rejected(self):
        manifest,raw=sample()
        data=validate_v2(manifest,raw)
        data["definitions"][0]["meanings"][0].pop("subject")
        changed=(json.dumps(data,sort_keys=True)+"\n").encode()
        update=dict(manifest,sha256=hashlib.sha256(changed).hexdigest())
        update["version"]="sha256:"+update["sha256"]
        with self.assertRaisesRegex(ValueError,"Subject"):
            validate_v2(update,changed)
        data["definitions"][0]["meanings"][0]["subject"]="Topology"
        data.pop("consolidated_ids")
        changed=(json.dumps(data,sort_keys=True)+"\n").encode()
        update=dict(manifest,sha256=hashlib.sha256(changed).hexdigest())
        update["version"]="sha256:"+update["sha256"]
        with self.assertRaisesRegex(ValueError,"redirect"):
            validate_v2(update,changed)

if __name__=="__main__":
    unittest.main()
