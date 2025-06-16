NearGravity API Flow Structure

Your three-API minimal case maps perfectly to the system's core functionality:

1. `/inject` - Campaign Publishing API
- **Purpose**: Publishers submit advertising campaigns
- **Process**: 
  - Campaign content is received
  - Content is embedded into vectors using the Semantic Service
  - Vectors are stored in the Message Store (VectorDB)
- **Actor**: Message Provider (advertiser/publisher)

2. `/guard` - Semantic Guard API
- **Purpose**: Users submit their semantic guard/intent
- **Process**:
  - User's intended meaning/context is captured
  - This creates a "signed" semantic boundary for the session
  - Stored in Intent Store for matching
- **Actor**: End User (optional)
- **Note**: Not always required as intent can be derived from messages

3. `/message` - Message Flow API
- **Purpose**: Process ongoing user messages
- **Process**:
  - User messages are embedded
  - Semantic matching occurs against injections
  - Augmented content is generated
  - Semantic integrity is verified against guard/intent
  - Final message is delivered if within semantic distance
- **Actor**: End User

## Key Architectural Considerations

### When Guard is Not Used
- Intent is derived directly from the message flow
- System uses implicit semantic matching
- More flexible but less constrained

### Semantic Integrity Verification
- Every augmentation is checked against:
  - Original user intent (explicit via guard or implicit via messages)
  - Semantic distance threshold
  - Ensures augmented content maintains user's core meaning

System Components Involved
Based on the architecture:
- **Semantic Agent**: Handles embeddings and semantic operations
- **Matching Agent**: Performs intent/injection matching
- **Delivery Agent**: Generates and formats final content
- **VectorDB**: Stores injection embeddings
- **Intent Store**: Manages user intents and matching patterns

This minimal API structure provides the essential functionality while maintaining the system's core promise of semantic integrity and privacy-preserving augmentation.