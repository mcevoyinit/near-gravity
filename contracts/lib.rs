use near_sdk::near;

#[near(contract_state)]
#[derive(Default)]
pub struct BlobStorage {
    count: u64,
}

#[near]
impl BlobStorage {
    // Just store data as blobs and increment counter
    pub fn store_blob(&mut self, data: String) -> u64 {
        self.count += 1;
        near_sdk::env::log_str(&format!("Stored blob #{}: {}", self.count, data));
        self.count
    }

    pub fn get_count(&self) -> u64 {
        self.count
    }
}