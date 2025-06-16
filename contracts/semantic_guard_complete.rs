/*
 * NEAR Semantic Guard Smart Contract - Complete Implementation
 * 
 * This contract demonstrates the full integration between NearGravity's RAG system
 * and NEAR blockchain for semantic analysis verification and storage.
 * 
 * Integrates with:
 * - src/models/dto/rag_models.rs (RAG data transfer objects)
 * - src/services/ai/semantic_service.rs (semantic analysis)
 * - src/matching_engine/ (similarity algorithms)
 * - src/hack/ hackathon package
 */

use near_sdk::borsh::{self, BorshDeserialize, BorshSerialize};
use near_sdk::collections::{LookupMap, UnorderedMap};
use near_sdk::serde::{Deserialize, Serialize};
use near_sdk::{env, near_bindgen, AccountId, PanicOnDefault, Promise, CryptoHash};
use std::collections::HashMap;

// ============================================================================
// NEARGRAVITY DTO INTEGRATION
// ============================================================================
// These types mirror the data structures from NearGravity's core system

/// Mirrors src/models/dto/rag_models.rs::SemanticDelta
#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct SemanticDelta {
    pub similarity_score: f64,
    pub confidence_level: f64,
    pub transformation_type: String,
    pub semantic_distance: f64,
    pub integrity_verified: bool,
}

/// Mirrors src/models/dto/rag_models.rs::MessageEmbedding
#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct MessageEmbedding {
    pub vector: Vec<f64>,
    pub model_name: String,
    pub embedding_hash: String,
    pub semantic_hash: String,
    pub timestamp: u64,
}

/// Mirrors src/services/ai/semantic_service.rs patterns
#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct SemanticAnalysisResult {
    pub center_of_gravity: String,
    pub outliers: Vec<SemanticOutlier>,
    pub distance_matrix: HashMap<String, f64>,
    pub embeddings: Vec<MessageEmbedding>,
    pub threshold_used: f64,
    pub processing_time_ms: u64,
    pub consensus_score: f64,
}

/// Extends NearGravity's outlier detection with blockchain verification
#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct SemanticOutlier {
    pub result_id: String,
    pub reason: String,
    pub severity: OutlierSeverity,
    pub max_distance: f64,
    pub source_type: String,
    pub verification_status: VerificationStatus,
    pub outlier_distances: Vec<OutlierDistance>,
}

#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct OutlierDistance {
    pub to_result: String,
    pub distance: f64,
    pub threshold_exceeded_by: f64,
}

#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub enum OutlierSeverity {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub enum VerificationStatus {
    Pending,
    Verified,
    Disputed,
    Flagged,
}

/// Search result with semantic metadata
#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct SearchResult {
    pub id: String,
    pub title: String,
    pub snippet: String,
    pub url: String,
    pub rank: u32,
    pub source_type: String,
    pub semantic_hash: String,
    pub trustworthiness_score: f64,
}

/// Complete semantic guard analysis record
#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct SemanticGuardRecord {
    pub id: String,
    pub query: String,
    pub results: Vec<SearchResult>,
    pub semantic_analysis: SemanticAnalysisResult,
    pub submitter: AccountId,
    pub timestamp: u64,
    pub block_height: u64,
    pub metadata: AnalysisMetadata,
}

#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct AnalysisMetadata {
    pub model_version: String,
    pub algorithm_version: String,
    pub processing_node: String,
    pub verification_count: u32,
    pub dispute_count: u32,
    pub consensus_reached: bool,
}

// ============================================================================
// MAIN CONTRACT
// ============================================================================

#[near_bindgen]
#[derive(BorshDeserialize, BorshSerialize, PanicOnDefault)]
pub struct SemanticGuardContract {
    /// Stored semantic analysis records
    pub analyses: UnorderedMap<String, SemanticGuardRecord>,
    
    /// Global contract metadata
    pub contract_metadata: ContractMetadata,
}

#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct ContractMetadata {
    pub version: String,
    pub total_analyses: u64,
    pub total_staked: u128,
    pub consensus_threshold: f64,
}

#[near_bindgen]
impl SemanticGuardContract {
    #[init]
    pub fn new() -> Self {
        Self {
            analyses: UnorderedMap::new(b"a"),
            contract_metadata: ContractMetadata {
                version: "1.0.0".to_string(),
                total_analyses: 0,
                total_staked: 0,
                consensus_threshold: 0.75,
            },
        }
    }

    // ========================================================================
    // SEMANTIC ANALYSIS STORAGE
    // ========================================================================

    /// Submit semantic analysis results to blockchain for verification
    #[payable]
    pub fn submit_semantic_analysis(
        &mut self,
        query: String,
        results: Vec<SearchResult>,
        semantic_analysis: SemanticAnalysisResult,
        metadata: AnalysisMetadata,
    ) -> String {
        let analysis_id = self.generate_analysis_id(&query);
        
        let record = SemanticGuardRecord {
            id: analysis_id.clone(),
            query,
            results,
            semantic_analysis,
            submitter: env::predecessor_account_id(),
            timestamp: env::block_timestamp(),
            block_height: env::block_index(),
            metadata,
        };

        self.analyses.insert(&analysis_id, &record);
        self.contract_metadata.total_analyses += 1;

        env::log_str(&format!("Semantic analysis stored: {}", analysis_id));
        analysis_id
    }

    /// Retrieve semantic analysis by ID
    pub fn get_semantic_analysis(&self, analysis_id: String) -> Option<SemanticGuardRecord> {
        self.analyses.get(&analysis_id)
    }

    /// Get analyses with outliers above threshold
    pub fn get_high_risk_analyses(&self, severity_threshold: OutlierSeverity) -> Vec<SemanticGuardRecord> {
        self.analyses
            .values()
            .filter(|record| {
                record.semantic_analysis.outliers.iter().any(|outlier| {
                    matches!(
                        (&outlier.severity, &severity_threshold),
                        (OutlierSeverity::Critical, _) |
                        (OutlierSeverity::High, OutlierSeverity::High | OutlierSeverity::Medium | OutlierSeverity::Low) |
                        (OutlierSeverity::Medium, OutlierSeverity::Medium | OutlierSeverity::Low) |
                        (OutlierSeverity::Low, OutlierSeverity::Low)
                    )
                })
            })
            .collect()
    }

    // ========================================================================
    // HACKATHON DEMO METHODS
    // ========================================================================

    /// Submit simplified analysis for hackathon demo
    pub fn submit_demo_analysis(
        &mut self,
        prefix: String,
        identifier: String,
        analysis_data: String,
    ) -> String {
        let storage_key = format!("{}_{}_demo", prefix, identifier);
        
        // Create simplified record for demo
        let demo_record = SemanticGuardRecord {
            id: storage_key.clone(),
            query: "Demo Query".to_string(),
            results: vec![],
            semantic_analysis: SemanticAnalysisResult {
                center_of_gravity: "A".to_string(),
                outliers: vec![],
                distance_matrix: HashMap::new(),
                embeddings: vec![],
                threshold_used: 0.75,
                processing_time_ms: 100,
                consensus_score: 0.95,
            },
            submitter: env::predecessor_account_id(),
            timestamp: env::block_timestamp(),
            block_height: env::block_index(),
            metadata: AnalysisMetadata {
                model_version: "demo".to_string(),
                algorithm_version: "1.0".to_string(),
                processing_node: "demo_node".to_string(),
                verification_count: 0,
                dispute_count: 0,
                consensus_reached: true,
            },
        };

        self.analyses.insert(&storage_key, &demo_record);
        self.contract_metadata.total_analyses += 1;

        env::log_str(&format!("Demo analysis stored: {}", storage_key));
        storage_key
    }

    /// Health check for demo
    pub fn health_check(&self) -> bool {
        true
    }

    // ========================================================================
    // INTERNAL HELPER METHODS
    // ========================================================================

    fn generate_analysis_id(&self, query: &str) -> String {
        let timestamp = env::block_timestamp();
        let hash_input = format!("{}{}{}", query, timestamp, env::predecessor_account_id());
        let hash = env::sha256(hash_input.as_bytes());
        near_sdk::bs58::encode(hash).into_string()
    }

    // ========================================================================
    // PUBLIC QUERY METHODS
    // ========================================================================

    pub fn get_contract_stats(&self) -> ContractMetadata {
        self.contract_metadata.clone()
    }

    pub fn get_total_analyses(&self) -> u64 {
        self.contract_metadata.total_analyses
    }

    pub fn get_recent_analyses(&self, limit: u32) -> Vec<SemanticGuardRecord> {
        self.analyses
            .values()
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
            .take(limit as usize)
            .collect()
    }
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use near_sdk::test_utils::{accounts, VMContextBuilder};
    use near_sdk::{testing_env, MockedBlockchain};

    fn get_context(predecessor_account_id: AccountId) -> VMContextBuilder {
        let mut builder = VMContextBuilder::new();
        builder
            .current_account_id(accounts(0))
            .signer_account_id(predecessor_account_id.clone())
            .predecessor_account_id(predecessor_account_id);
        builder
    }

    #[test]
    fn test_semantic_analysis_storage() {
        let context = get_context(accounts(1));
        testing_env!(context.build());

        let mut contract = SemanticGuardContract::new();
        
        let results = vec![SearchResult {
            id: "A".to_string(),
            title: "Test Result".to_string(),
            snippet: "Test snippet".to_string(),
            url: "https://test.com".to_string(),
            rank: 1,
            source_type: "scientific".to_string(),
            semantic_hash: "hash123".to_string(),
            trustworthiness_score: 0.9,
        }];

        let analysis = SemanticAnalysisResult {
            center_of_gravity: "A".to_string(),
            outliers: vec![],
            distance_matrix: HashMap::new(),
            embeddings: vec![],
            threshold_used: 0.75,
            processing_time_ms: 100,
            consensus_score: 0.95,
        };

        let metadata = AnalysisMetadata {
            model_version: "1.0".to_string(),
            algorithm_version: "1.0".to_string(),
            processing_node: "node1".to_string(),
            verification_count: 0,
            dispute_count: 0,
            consensus_reached: false,
        };

        let analysis_id = contract.submit_semantic_analysis(
            "test query".to_string(),
            results,
            analysis,
            metadata,
        );

        assert!(contract.get_semantic_analysis(analysis_id).is_some());
        assert_eq!(contract.contract_metadata.total_analyses, 1);
    }

    #[test]
    fn test_demo_functionality() {
        let context = get_context(accounts(1));
        testing_env!(context.build());

        let mut contract = SemanticGuardContract::new();
        
        let storage_key = contract.submit_demo_analysis(
            "semantic_guard".to_string(),
            "demo_test".to_string(),
            "{}".to_string(),
        );

        assert!(contract.get_semantic_analysis(storage_key).is_some());
        assert!(contract.health_check());
        assert_eq!(contract.get_total_analyses(), 1);
    }
}