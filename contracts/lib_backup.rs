use near_sdk::near;
use std::collections::HashMap;

#[near(contract_state)]
pub struct NearGravitySemanticGuard {
    owner: String,
    total_analyses: u64,
    // Store analysis data as JSON strings for simplicity 
    analyses: HashMap<String, String>,
}

impl Default for NearGravitySemanticGuard {
    fn default() -> Self {
        Self {
            owner: "NearGravity.near".to_string(),
            total_analyses: 0,
            analyses: HashMap::new(),
        }
    }
}

#[near]
impl NearGravitySemanticGuard {
    #[init]
    pub fn new(owner: String) -> Self {
        Self {
            owner,
            total_analyses: 0,
            analyses: HashMap::new(),
        }
    }

    #[init(ignore_state)]
    pub fn migrate() -> Self {
        // Migration function to handle state changes
        Self {
            owner: "NearGravity.near".to_string(),
            total_analyses: 0,
            analyses: HashMap::new(),
        }
    }

    pub fn get_owner(&self) -> String {
        self.owner.clone()
    }

    pub fn get_stats(&self) -> HashMap<String, u64> {
        let mut stats = HashMap::new();
        stats.insert("total_analyses".to_string(), self.total_analyses);
        stats.insert("total_stored".to_string(), self.analyses.len() as u64);
        stats
    }

    pub fn store_semantic_analysis(&mut self, analysis_id: String, analysis_json: String) -> String {
        if analysis_id.is_empty() {
            near_sdk::env::panic_str("Analysis ID cannot be empty");
        }

        if analysis_json.is_empty() {
            near_sdk::env::panic_str("Analysis JSON cannot be empty");
        }

        self.total_analyses += 1;
        self.analyses.insert(analysis_id.clone(), analysis_json);

        near_sdk::env::log_str(&format!(
            "Stored semantic analysis: {} (total: {})", 
            analysis_id, 
            self.total_analyses
        ));

        format!("analysis_{}", self.total_analyses)
    }

    pub fn get_semantic_analysis(&self, analysis_id: String) -> Option<String> {
        self.analyses.get(&analysis_id).cloned()
    }

    pub fn search_by_query(&self, query: String) -> Vec<String> {
        let query_lower = query.to_lowercase();
        self.analyses
            .iter()
            .filter(|(_, data)| data.to_lowercase().contains(&query_lower))
            .map(|(id, _)| id.clone())
            .collect()
    }

    pub fn get_recent_analyses(&self, limit: u32) -> Vec<String> {
        // Return most recent analysis IDs (simplified implementation)
        let mut ids: Vec<String> = self.analyses.keys().cloned().collect();
        ids.sort();
        ids.into_iter()
            .rev()
            .take(limit as usize)
            .collect()
    }

    pub fn increment(&mut self) -> u64 {
        self.total_analyses += 1;
        self.total_analyses
    }

    pub fn delete_analysis(&mut self, analysis_id: String) -> bool {
        self.analyses.remove(&analysis_id).is_some()
    }
}