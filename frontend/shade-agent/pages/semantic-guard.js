import Head from 'next/head';
import { useState, useRef, useEffect } from 'react';
import styles from '../styles/SemanticGuard.module.css';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function SemanticGuard() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [semanticAnalysis, setSemanticAnalysis] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [searchHistory, setSearchHistory] = useState([]);
    const inputRef = useRef(null);

    const performSearch = async (searchQuery = query.trim()) => {
        if (!searchQuery) return;

        setIsLoading(true);
        setError('');
        
        try {
            const response = await fetch(`${API_BASE_URL}/near/semantic-guard`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: searchQuery,
                    max_results: 5,
                    semantic_threshold: 0.75,
                    use_mock_search: true // For demo purposes
                })
            });

            if (!response.ok) {
                throw new Error(`Search failed: ${response.status}`);
            }

            const data = await response.json();
            setResults(data.results || []);
            setSemanticAnalysis(data.semantic_analysis || null);
            
            // Add to search history
            setSearchHistory(prev => [
                { query: searchQuery, timestamp: Date.now() },
                ...prev.slice(0, 4) // Keep last 5 searches
            ]);

        } catch (err) {
            console.error('Search error:', err);
            setError('Search failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        performSearch();
    };

    const formatDistance = (distance) => {
        return (distance * 100).toFixed(1) + '%';
    };

    const getResultClassName = (result) => {
        let className = styles.result;
        if (result.is_center_of_gravity) {
            className += ` ${styles.centerOfGravity}`;
        } else if (result.is_outlier) {
            // Color code outliers based on source type and severity
            const sourceType = result.source_type;
            if (sourceType === 'conspiracy') {
                className += ` ${styles.outlierDanger}`;
            } else if (sourceType === 'alarmist') {
                className += ` ${styles.outlierWarning}`;
            } else if (['economic', 'policy'].includes(sourceType)) {
                className += ` ${styles.outlierCaution}`;
            } else {
                className += ` ${styles.outlierMild}`;
            }
        } else {
            // Non-outlier, trusted sources get subtle green accent
            className += ` ${styles.trustedSource}`;
        }
        return className;
    };

    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.focus();
        }
    }, []);

    return (
        <div className={styles.container}>
            <Head>
                <title>Semantic Guard - NearGravity</title>
                <meta name="description" content="AI-powered semantic analysis of search results" />
                <link rel="icon" href="/favicon.ico" />
            </Head>

            <div className={styles.header}>
                <h1 className={styles.title}>
                    NEAR Semantic Gravity Guard
                </h1>
                <p className={styles.subtitle}>
                    Private, tamper-proof AI-powered semantic verification.
                </p>
            </div>

            <div className={styles.searchContainer}>
                <form onSubmit={handleSubmit} className={styles.searchForm}>
                    <div className={styles.inputWrapper}>
                        <input
                            ref={inputRef}
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="What would you like to search for?"
                            className={styles.searchInput}
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            className={styles.searchButton}
                            disabled={isLoading || !query.trim()}
                        >
                            {isLoading ? 'Searching...' : 'Search'}
                        </button>
                    </div>
                </form>

                {searchHistory.length > 0 && (
                    <div className={styles.searchHistory}>
                        <span>Recent searches:</span>
                        {searchHistory.map((item, index) => (
                            <button
                                key={index}
                                onClick={() => {
                                    setQuery(item.query);
                                    performSearch(item.query);
                                }}
                                className={styles.historyItem}
                            >
                                {item.query}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {error && (
                <div className={styles.error}>
                    {error}
                </div>
            )}

            {isLoading && (
                <div className={styles.loading}>
                    <div className={styles.loadingSpinner}></div>
                    <p>Analyzing semantic relationships...</p>
                </div>
            )}

            {semanticAnalysis && (
                <div className={styles.analysisContainer}>
                    <div className={styles.analysisHeader}>
                        <h2>Semantic Analysis</h2>
                        <div className={styles.analysisStats}>
                            <span className={styles.stat}>
                                <strong>{semanticAnalysis.embeddings_generated}</strong> results analyzed
                            </span>
                            <span className={styles.stat}>
                                <strong>{semanticAnalysis.total_comparisons}</strong> comparisons
                            </span>
                            <span className={styles.stat}>
                                <strong>{semanticAnalysis.processing_time_ms}ms</strong> processing time
                            </span>
                        </div>
                    </div>

                    <div className={styles.analysisGrid}>
                        <div className={styles.centerOfGravityCard}>
                            <h3>Center of Gravity</h3>
                            <p>
                                Result <strong>{semanticAnalysis.center_of_gravity.result_id}</strong> has 
                                the minimum average semantic distance to all other results
                            </p>
                        </div>

                        <div className={styles.outliersCard}>
                            <h3>
                                Outliers Detected
                                {(() => {
                                    const scenario = results[0]?.scenario;
                                    if (scenario === 'high_trust') return ' 🟢';
                                    if (scenario === 'misinformation_detected') return ' 🔴';
                                    if (scenario === 'mixed_signals') return ' 🟡';
                                    if (scenario === 'economic_uncertainty') return ' 🟠';
                                    return '';
                                })()}
                            </h3>
                            {semanticAnalysis.outliers.length > 0 ? (
                                <div>
                                    <p><strong>{semanticAnalysis.outliers.length}</strong> outliers found</p>
                                    {semanticAnalysis.outliers.map((outlier, index) => (
                                        <div key={index} className={styles.outlierItem}>
                                            <div className={styles.outlierContent}>
                                                <span className={styles.outlierLabel}>
                                                    Result {outlier.result_id}
                                                </span>
                                                <p className={styles.outlierReason}>
                                                    {outlier.reason}
                                                </p>
                                            </div>
                                            <span className={`${styles.severityBadge} ${styles[outlier.severity]}`}>
                                                {outlier.severity}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className={styles.noOutliers}>
                                    <p>✅ No semantic outliers detected</p>
                                    <p className={styles.trustMessage}>
                                        All sources show high semantic consistency
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {results.length > 0 && (
                <div className={styles.resultsContainer}>
                    <h2 className={styles.resultsHeader}>Search Results</h2>
                    <div className={styles.resultsList}>
                        {results.map((result, index) => (
                            <div key={result.id} className={getResultClassName(result)}>
                                <div className={styles.resultHeader}>
                                    <div className={styles.resultMeta}>
                                        <span className={styles.resultRank}>#{result.rank}</span>
                                        <span className={styles.resultId}>{result.id}</span>
                                        {result.is_center_of_gravity && (
                                            <span className={styles.badge + ' ' + styles.gravityBadge}>
                                                ⭐ Center of Gravity
                                            </span>
                                        )}
                                        {result.is_outlier && (
                                            <span className={`${styles.badge} ${(() => {
                                                const sourceType = result.source_type;
                                                if (sourceType === 'conspiracy') return styles.dangerBadge;
                                                if (sourceType === 'alarmist') return styles.warningBadge;
                                                if (['economic', 'policy'].includes(sourceType)) return styles.cautionBadge;
                                                return styles.outlierBadge;
                                            })()}`}>
                                                {(() => {
                                                    const sourceType = result.source_type;
                                                    if (sourceType === 'conspiracy') return '🚨 Misinformation Risk';
                                                    if (sourceType === 'alarmist') return '⚠️ Sensationalized';
                                                    if (sourceType === 'economic') return '📊 Economic Dispute';
                                                    if (sourceType === 'policy') return '⚖️ Policy Debate';
                                                    return '❓ Semantic Outlier';
                                                })()}
                                            </span>
                                        )}
                                        {!result.is_outlier && !result.is_center_of_gravity && (
                                            <span className={styles.badge + ' ' + styles.trustedBadge}>
                                                ✅ Trusted Source
                                            </span>
                                        )}
                                        
                                        {/* Source type indicator */}
                                        <span className={`${styles.sourceTypeBadge} ${styles[result.source_type] || styles.unknown}`}>
                                            {(() => {
                                                const type = result.source_type;
                                                if (type === 'scientific') return '🔬 Scientific';
                                                if (type === 'health_authority') return '🏥 Health Authority';
                                                if (type === 'medical') return '⚕️ Medical';
                                                if (type === 'conspiracy') return '🕳️ Conspiracy';
                                                if (type === 'alarmist') return '📢 Alarmist';
                                                if (type === 'government') return '🏛️ Government';
                                                if (type === 'financial') return '💰 Financial';
                                                if (type === 'central_bank') return '🏦 Central Bank';
                                                if (type === 'economic') return '📈 Economic';
                                                if (type === 'tech_news') return '💻 Tech News';
                                                if (type === 'education') return '🎓 Education';
                                                if (type === 'policy') return '📋 Policy';
                                                if (type === 'institutional') return '🏢 Institutional';
                                                return '📰 News';
                                            })()}
                                        </span>
                                    </div>
                                    <div className={styles.semanticScore}>
                                        Distance: {formatDistance(result.gravity_score)}
                                    </div>
                                </div>
                                
                                <h3 className={styles.resultTitle}>
                                    <a href={result.url} target="_blank" rel="noopener noreferrer">
                                        {result.title}
                                    </a>
                                </h3>
                                
                                <p className={styles.resultSnippet}>
                                    {result.snippet}
                                </p>
                                
                                <div className={styles.resultFooter}>
                                    <span className={styles.resultUrl}>
                                        {new URL(result.url).hostname}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {results.length === 0 && !isLoading && !error && (
                <div className={styles.emptyState}>
                    <h2>Welcome to Semantic Guard</h2>
                    <p>
                        Enter a search query to see AI-powered semantic analysis of results.
                        Our system identifies the most representative result (center of gravity)
                        and detects semantic outliers that may contain misinformation.
                    </p>
                    <div className={styles.exampleQueries}>
                        <p>Try these example scenarios:</p>
                        
                        <div className={styles.scenarioGrid}>
                            <div className={styles.scenarioCard}>
                                <div className={styles.scenarioHeader}>
                                    <span className={`${styles.scenarioIndicator} ${styles.greenIndicator}`}>●</span>
                                    <span className={styles.scenarioTitle}>High Trust</span>
                                </div>
                                <p className={styles.scenarioDesc}>All sources align - no outliers detected</p>
                                <button
                                    onClick={() => {
                                        setQuery('climate change latest research');
                                        performSearch('climate change latest research');
                                    }}
                                    className={styles.exampleQuery}
                                >
                                    climate change latest research
                                </button>
                            </div>

                            <div className={styles.scenarioCard}>
                                <div className={styles.scenarioHeader}>
                                    <span className={`${styles.scenarioIndicator} ${styles.redIndicator}`}>●</span>
                                    <span className={styles.scenarioTitle}>Misinformation Alert</span>
                                </div>
                                <p className={styles.scenarioDesc}>Potential misinformation detected</p>
                                <button
                                    onClick={() => {
                                        setQuery('covid vaccine safety');
                                        performSearch('covid vaccine safety');
                                    }}
                                    className={styles.exampleQuery}
                                >
                                    covid vaccine safety
                                </button>
                            </div>

                            <div className={styles.scenarioCard}>
                                <div className={styles.scenarioHeader}>
                                    <span className={`${styles.scenarioIndicator} ${styles.yellowIndicator}`}>●</span>
                                    <span className={styles.scenarioTitle}>Mixed Signals</span>
                                </div>
                                <p className={styles.scenarioDesc}>Conflicting viewpoints present</p>
                                <button
                                    onClick={() => {
                                        setQuery('artificial intelligence jobs');
                                        performSearch('artificial intelligence jobs');
                                    }}
                                    className={styles.exampleQuery}
                                >
                                    artificial intelligence jobs
                                </button>
                            </div>

                            <div className={styles.scenarioCard}>
                                <div className={styles.scenarioHeader}>
                                    <span className={`${styles.scenarioIndicator} ${styles.orangeIndicator}`}>●</span>
                                    <span className={styles.scenarioTitle}>Economic Uncertainty</span>
                                </div>
                                <p className={styles.scenarioDesc}>Sensationalized claims detected</p>
                                <button
                                    onClick={() => {
                                        setQuery('economy recession 2024');
                                        performSearch('economy recession 2024');
                                    }}
                                    className={styles.exampleQuery}
                                >
                                    economy recession 2024
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <footer className={styles.footer}>
                <p>
                    Powered by <strong>NearGravity</strong> × <strong>NEAR Protocol</strong>
                </p>
            </footer>
        </div>
    );
}