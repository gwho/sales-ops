CREATE TABLE workflow_results (
    session_id UUID NOT NULL,
    workflow_type TEXT NOT NULL,
    result JSONB NOT NULL,
    result_schema_version INTEGER NOT NULL,
    saved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (session_id, workflow_type),
    CHECK (
        workflow_type IN (
            'order_validation',
            'inventory_allocation',
            'payment_aging'
        )
    )
);
