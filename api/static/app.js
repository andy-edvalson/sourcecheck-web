// Alpine.js app
function validatorApp() {
    return {
        sourceText: `The quarterly earnings call took place on Tuesday morning at 9 AM EST. CEO Sarah Chen announced that revenue grew by 12% year-over-year, reaching $45 million in Q3. The company hired 25 new employees across engineering and sales departments. Customer retention rate improved to 89%, up from 85% last quarter. The product team launched two new features in September. Operating expenses increased by 8% due to expanded marketing efforts. The board approved a $5 million investment in R&D for the next fiscal year.`,
        claims: `The company's Q3 earnings call revealed strong performance with revenue growing 15% to $48 million. CEO Sarah Chen highlighted the addition of 30 new team members and announced three major product launches in September. Customer retention reached an impressive 92%, and the board committed $8 million to future R&D initiatives.`,
        schema: '',
        policies: '',
        showConfig: false,
        loading: false,
        results: null,
        error: null,

        async init() {
            // Load default schema and policies
            try {
                const [schemaRes, policiesRes] = await Promise.all([
                    fetch('/static/defaults/schema.yaml'),
                    fetch('/static/defaults/policies.yaml')
                ]);
                
                this.schema = await schemaRes.text();
                this.policies = await policiesRes.text();
            } catch (err) {
                console.error('Failed to load defaults:', err);
            }
        },

        async validateClaims() {
            this.loading = true;
            this.error = null;
            this.results = null;

            try {
                // Parse YAML to JSON
                const schemaObj = jsyaml.load(this.schema);
                const policiesObj = jsyaml.load(this.policies);
                
                // Try to parse as JSON, if it fails treat as plain text
                let claimsObj;
                try {
                    claimsObj = JSON.parse(this.claims);
                } catch (e) {
                    // Not JSON - wrap plain text in {"body": "text"}
                    claimsObj = { "body": this.claims.trim() };
                }

                // Make API request
                const response = await fetch('/api/v1/validate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        source_text: this.sourceText,
                        claims: claimsObj,
                        schema: schemaObj,
                        policies: policiesObj
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Validation failed');
                }

                this.results = await response.json();
            } catch (err) {
                this.error = err.message;
                console.error('Validation error:', err);
            } finally {
                this.loading = false;
            }
        },

        getScoreClass(score) {
            if (!score) return 'low';
            if (score >= 0.7) return 'high';
            if (score >= 0.4) return 'medium';
            return 'low';
        }
    };
}
