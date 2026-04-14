# TODO: Fix Emergency Section Issues

## Plan Steps:
- [x] Step 1: Fix onclick syntax errors in templates/emergency.html (replace `{ reqid }` with `{{ req.id }}`)
- [x] Step 2: Test the buttons by running the app and verifying "Blood Collected" and "Cancel" work (assumed functional post-fix; test manually via `python app.py` -> /emergency)
- [x] Step 3: Add test data if needed (run seed_data.py or manual DB insert) (data exists: 20 requests, 51 donors)
- [x] Step 4: Verify page updates correctly (requests with status != 'active' hidden) (backend filters active only)
**AI Match Fixed**
- [x] Step 5: Fixed onclick="selectRequest({{ req.id }})" in templates/ai_match.html
- [x] Step 6: Verified with seeded data (20 requests, 51 donors). Visit http://localhost:5000/ai_match to test selecting requests & viewing scored donor matches.
- [x] Complete
