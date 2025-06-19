// mushi-frontend/src/components/data/DataClusterViewer.jsx
import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
import * as d3 from 'd3';
import { useNavigate } from 'react-router-dom';

const InspectorPanel = ({ node, onClose }) => {
    if (!node) return null;
    const navigate = useNavigate();

    const handleViewDetails = () => {
        if (node.id) {
            navigate(`/anime/details/${node.id}`);
        }
    };

    return (
        <div className="absolute top-4 right-4 bg-neutral-900/80 backdrop-blur-md w-72 rounded-xl shadow-2xl border border-white/10 p-4 z-20 animate-[fadeIn_0.3s_ease-out]">
            <button onClick={onClose} className="absolute top-2 right-2 text-gray-400 hover:text-white p-1 rounded-full">×</button>
            <img src={node.poster} alt={node.name} className="w-full h-40 object-cover rounded-lg mb-3" />
            <h3 className="font-bold text-lg text-white">{node.name}</h3>
            {node.clusterTitle && <p className="text-sm text-gray-300">Cluster: <span style={{ color: node.clusterColor }}>{node.clusterTitle}</span></p>}
            {node.id && (
                <button onClick={handleViewDetails} className="mt-4 w-full bg-pink-500 hover:bg-pink-600 text-white font-bold py-2 px-4 rounded-lg transition-colors">
                    View Details
                </button>
            )}
        </div>
    );
};

function DataClusterViewer() {
    const svgRef = useRef(null);
    const containerRef = useRef(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isDataEmpty, setIsDataEmpty] = useState(false);
    const [numClusters, setNumClusters] = useState('5');
    const [triggerFetch, setTriggerFetch] = useState(5);
    const [selectedNode, setSelectedNode] = useState(null);
    const [loadingProgress, setLoadingProgress] = useState(0);

    const clusterColors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#EF4444', '#3B82F6', '#F59E0B', '#10B981', '#636e72', '#fd79a8'
    ];

    useEffect(() => {
        const handler = setTimeout(() => {
            const parsedNum = parseInt(numClusters);
            if (!isNaN(parsedNum) && parsedNum >= 2 && parsedNum <= 12) {
                setTriggerFetch(parsedNum);
            }
        }, 800);
        return () => clearTimeout(handler);
    }, [numClusters]);

    useEffect(() => {
        let isMounted = true;
        const fetchDataAndDraw = async () => {
            if (!isMounted) return;
            setIsLoading(true);
            setError(null);
            setIsDataEmpty(false);
            setSelectedNode(null);
            setLoadingProgress(0);

            const progressInterval = setInterval(() => {
                setLoadingProgress(prev => Math.min(prev + 1, 95));
            }, 300);

            try {
                // Fetch both data sources concurrently
                const [homeDataResponse, clusterData] = await Promise.all([
                    api.anime.getHomeData(),
                    api.data.getClusteredData(triggerFetch)
                ]);

                if (!isMounted) return;
                clearInterval(progressInterval);
                setLoadingProgress(100);

                if (clusterData.error) {
                    if (clusterData.error.includes("not available yet")) {
                        setIsDataEmpty(true);
                    } else {
                        setError(clusterData.error);
                    }
                    return;
                }

                const allAnime = [
                    ...homeDataResponse.spotlights, ...homeDataResponse.trending,
                    ...homeDataResponse.top_airing, ...homeDataResponse.most_popular,
                    ...homeDataResponse.most_favorite,
                ];
                const uniqueAnime = [...new Map(allAnime.map(item => [item.id, item])).values()];

                const { doc_id_to_label, cluster_info } = clusterData;

                const nodes = [];
                Object.keys(cluster_info).forEach(clusterIdStr => {
                    const id = parseInt(clusterIdStr);
                    nodes.push({
                        id: `cluster-${id}`, type: 'cluster', name: cluster_info[id].title,
                        size: 20 + (cluster_info[id]?.top_terms?.length || 0) * 5,
                        color: clusterColors[id % clusterColors.length],
                    });
                });

                const docNodes = uniqueAnime.map(anime => {
                    const source_id = `anime_api_details_${anime.id}`;
                    const clusterLabel = doc_id_to_label[source_id];

                    const baseColor = d3.color(clusterLabel !== undefined ? clusterColors[clusterLabel % clusterColors.length] : "#555");
                    // --- D3 BUG FIX: Use hsl() for color modification ---
                    const modifiedColor = d3.hsl(baseColor);
                    modifiedColor.s = clusterLabel !== undefined ? modifiedColor.s : 0; // Don't oversaturate
                    modifiedColor.l = clusterLabel !== undefined ? modifiedColor.l + 0.1 : 0.4;
                    // --- END OF BUG FIX ---

                    return {
                        id: anime.id, type: 'document', name: anime.title,
                        poster: anime.poster_url || anime.poster, cluster: clusterLabel,
                        color: modifiedColor.toString(), size: 5,
                        clusterTitle: clusterLabel !== undefined ? cluster_info[clusterLabel].title : "Unclustered",
                        clusterColor: baseColor.toString()
                    };
                });

                nodes.push(...docNodes);
                const links = docNodes
                    .filter(doc => doc.cluster !== undefined)
                    .map(doc => ({ source: doc.id, target: `cluster-${doc.cluster}` }));

                if (!containerRef.current) return;
                const { width, height } = containerRef.current.getBoundingClientRect();
                const svg = d3.select(svgRef.current).html("").attr("viewBox", [-width / 2, -height / 2, width, height]);

                const simulation = d3.forceSimulation(nodes)
                    .force("link", d3.forceLink(links).id(d => d.id).strength(0.05).distance(40))
                    .force("charge", d3.forceManyBody().strength(-40))
                    .force("center", d3.forceCenter(0, 0))
                    .force("x", d3.forceX().strength(0.02))
                    .force("y", d3.forceY().strength(0.02))
                    .force("collide", d3.forceCollide().radius(d => d.size + 4));

                const g = svg.append("g");
                const linkElements = g.append("g").attr("stroke", "#999").attr("stroke-opacity", 0.1).selectAll("line").data(links).join("line");
                const nodeElements = g.append("g").selectAll("g.node").data(nodes, d => d.id).join("g").attr("class", "node").call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));

                function dragstarted(event, d) { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }
                function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
                function dragended(event, d) { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }

                nodeElements.append("circle").attr("r", d => d.size).attr("fill", d => d.color);
                nodeElements.filter(d => d.type === 'cluster').append("text")
                    .text(d => d.name).attr("text-anchor", "middle").attr("dy", d => -(d.size + 5))
                    .attr("fill", "#fff").attr("font-size", "14px").attr("font-weight", "bold")
                    .attr("paint-order", "stroke").attr("stroke", "#111827").attr("stroke-width", "0.3em").style("pointer-events", "none");

                nodeElements.on("click", (event, d) => { if (d.type === 'document') setSelectedNode(d); });
                simulation.on("tick", () => {
                    linkElements.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                    nodeElements.attr("transform", d => `translate(${d.x},${d.y})`);
                });

                const zoom = d3.zoom().scaleExtent([0.1, 8]).on("zoom", ({ transform }) => g.attr("transform", transform));
                svg.call(zoom);

            } catch (e) {
                if(isMounted) {
                    clearInterval(progressInterval);
                    setError(e.message);
                }
            } finally {
                if(isMounted) setIsLoading(false);
            }
        };

        fetchDataAndDraw();

        return () => {
            isMounted = false;
        };
    }, [triggerFetch]);

    const renderOverlay = () => {
        if (isLoading) {
             return (
                <div className="absolute inset-0 flex flex-col justify-center items-center text-indigo-300 text-lg bg-black/70 z-20 p-4 text-center">
                    <p>Mushi is mapping the data constellations... ☆</p>
                    <div className="w-1/2 max-w-sm mt-4 bg-gray-600 rounded-full h-2.5">
                        <div className="bg-gradient-to-r from-teal-400 to-cyan-400 h-2.5 rounded-full" style={{ width: `${loadingProgress}%`, transition: 'width 0.5s ease-out' }}></div>
                    </div>
                    <p className="text-sm mt-2 text-gray-400">Loading pre-computed data. This should be quick!</p>
                </div>
            )
        }
        if (isDataEmpty) {
            return (
                <div className="absolute inset-0 flex flex-col justify-center items-center text-center text-indigo-300 text-lg bg-black/50 z-20 p-4">
                    <p>Mushi is still learning about the anime universe!</p>
                    <p className="text-sm text-gray-400 mt-2">The database is being populated in the background. Please refresh in a few minutes.</p>
                </div>
            );
        }
        if (error) {
            return <div className="absolute inset-0 flex justify-center items-center text-red-400 text-lg p-4 text-center z-20">{error}</div>
        }
        return null;
    }

    return (
        <div className="p-4 bg-neutral-800/50 backdrop-blur-sm rounded-xl shadow-lg border border-purple-500/20">
            <div ref={containerRef} className="w-full h-[80vh] rounded-lg bg-[#111827] relative overflow-hidden">
                {renderOverlay()}
                <svg ref={svgRef} className="w-full h-full"></svg>

                <div className="absolute top-4 left-4 bg-neutral-900/70 backdrop-blur-sm p-4 rounded-lg shadow-lg w-72 z-20">
                     <label htmlFor="numClusters" className="block text-gray-300 font-medium mb-2 text-center">Number of Clusters:</label>
                     <input id="numClusters" type="number" min="2" max="10" value={numClusters}
                            onChange={e => setNumClusters(e.target.value)}
                            className="w-full p-2 rounded-md bg-gray-700 text-white text-center focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
                </div>
                <InspectorPanel node={selectedNode} onClose={() => setSelectedNode(null)} />
            </div>
        </div>
    );
}

export default DataClusterViewer;
