# Data directory

Run `python -m accountlens.data.generate` to create the reproducible synthetic dataset in `data/generated/`.

Generated records are intentionally excluded from Git because the generator, seed, reference date, and file hashes provide the reproducible source of truth.

Each account contains `true_signatory_contact_id`, defined as the contact with final commercial approval authority. This field is used only for offline evaluation and is removed from every model prompt to prevent label leakage.

`teacher_aligned_10/` is a separate, deterministic, hand-authored supplementary dataset built to match the instructor's requested evidence shape. Each of its ten accounts contains two email threads with CC lists, one attendee list, two tickets, one CRM note and an explicit true commercial signatory. See `docs/teacher_aligned_dataset.md`.
