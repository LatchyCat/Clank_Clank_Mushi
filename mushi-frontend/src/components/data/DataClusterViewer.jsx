// mushi-frontend/src/components/data/DataClusterViewer.jsx
import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api'; // Correct path to api.js
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'; // For interactive camera control

/**
 * DataClusterViewer component fetches and displays clustered data documents
 * in a 3D visualization using Three.js.
 */
function DataClusterViewer() {
  const mountRef = useRef(null); // Ref for the div where the Three.js scene will be mounted
  const [clusteredData, setClusteredData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [numClusters, setNumClusters] = useState(5); // Default number of clusters

  // Color palette for clusters (you can expand this for more clusters)
  const clusterColors = [
    0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0xff00ff, 0x00ffff, 0xff8800, 0x8800ff, 0x00ff88, 0x88ff00
  ];

  // --- Fetch Clustered Data ---
  useEffect(() => {
    const fetchClusteredData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await api.data.getClusteredData(numClusters);

        if (data && data.clustered_documents) {
          setClusteredData(data);
          console.log(`Mushi found sparkling clustered data with ${numClusters} clusters, desu!~`, data);
        } else {
          setError(`Muu... Mushi couldn't fetch clustered data with ${numClusters} clusters. Gomen'nasai! (T_T)`);
        }
      } catch (err) {
        console.error(`Uwaah! Failed to fetch clustered data with ${numClusters} clusters:`, err);
        setError(`Mushi encountered an error while fetching clustered data: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchClusteredData();
  }, [numClusters]); // Re-run effect when numClusters changes

  // --- Three.js Scene Setup ---
  useEffect(() => {
    if (!mountRef.current || isLoading || error || !clusteredData) return;

    const currentMount = mountRef.current;
    let scene, camera, renderer, controls;
    let animationFrameId; // To store the ID of the animation frame

    const initThree = () => {
      // Scene
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x1a202c); // Dark background similar to Tailwind gray-900

      // Camera
      camera = new THREE.PerspectiveCamera(
        75,
        currentMount.clientWidth / currentMount.clientHeight,
        0.1,
        1000
      );
      camera.position.z = 50; // Move camera back to see objects

      // Renderer
      renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
      currentMount.appendChild(renderer.domElement);

      // Controls (OrbitControls for interactive camera)
      controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true; // An animation loop is required when damping is enabled
      controls.dampingFactor = 0.05;

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5); // Soft white light
      scene.add(ambientLight);
      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight.position.set(0, 1, 1).normalize();
      scene.add(directionalLight);

      // --- Add 3D objects based on clustered data ---
      const clusterCenters = new Map(); // To store the average position for each cluster
      const clusterCounts = new Map(); // To store the number of documents in each cluster

      // First, calculate bounding box of document positions within each cluster
      // and determine average positions for initial cluster placement.
      // For simplicity, we'll just place them randomly within a sphere for now.

      const sphereRadius = 20; // Radius for distributing clusters

      Object.entries(clusteredData.clustered_documents).forEach(([clusterId, documents]) => {
        const clusterIndex = parseInt(clusterId, 10);
        const color = new THREE.Color(clusterColors[clusterIndex % clusterColors.length]);

        // Position clusters in a spherical arrangement
        // For a more meaningful visualization, you'd use embedding positions.
        // Here, we're just spreading them out for visual distinction.
        const angle = (clusterIndex / numClusters) * Math.PI * 2;
        const x = sphereRadius * Math.cos(angle);
        const y = sphereRadius * Math.sin(angle);
        const z = (Math.random() - 0.5) * 10; // Slight variation in Z

        // Create a representative object for the cluster (e.g., a larger sphere)
        const clusterGeometry = new THREE.SphereGeometry(1.5, 32, 32);
        const clusterMaterial = new THREE.MeshPhongMaterial({ color: color, transparent: true, opacity: 0.7 });
        const clusterMesh = new THREE.Mesh(clusterGeometry, clusterMaterial);
        clusterMesh.position.set(x, y, z);
        scene.add(clusterMesh);

        // Add a label for the cluster (basic text geometry, more advanced options exist)
        // This requires a font loader, which is more complex. For now, we'll skip 3D text.
        // You can use a CSS2DRenderer for HTML-based labels.

        // Place small spheres for each document within its cluster's vicinity
        documents.forEach((doc, docIndex) => {
          const docGeometry = new THREE.SphereGeometry(0.3, 16, 16);
          const docMaterial = new THREE.MeshPhongMaterial({ color: color.clone().offsetHSL(0, 0, 0.2), flatShading: true }); // Lighter shade
          const docMesh = new THREE.Mesh(docGeometry, docMaterial);

          // Position documents randomly around their cluster center
          const docOffsetX = (Math.random() - 0.5) * 5;
          const docOffsetY = (Math.random() - 0.5) * 5;
          const docOffsetZ = (Math.random() - 0.5) * 5;
          docMesh.position.set(x + docOffsetX, y + docOffsetY, z + docOffsetZ);
          scene.add(docMesh);

          // You could store references to these meshes and
          // attach data (e.g., doc.content) for interactivity (e.g., on click popups).
        });
      });

      // Animation loop
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        controls.update(); // only required if controls.enableDamping or controls.autoRotate are set to true
        renderer.render(scene, camera);
      };

      animate();

      // Handle window resize
      const handleResize = () => {
        camera.aspect = currentMount.clientWidth / currentMount.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
      };
      window.addEventListener('resize', handleResize);

      // Cleanup function
      return () => {
        cancelAnimationFrame(animationFrameId); // Stop the animation loop
        window.removeEventListener('resize', handleResize);
        if (currentMount) {
          currentMount.removeChild(renderer.domElement);
        }
        renderer.dispose();
        controls.dispose();
        // Dispose of geometries and materials if created inside the loop for performance
        scene.clear(); // Clear all objects from the scene
      };
    };

    initThree();
  }, [clusteredData, isLoading, error, numClusters]); // Re-initialize Three.js if data or parameters change

  const handleNumClustersChange = (e) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value > 0) {
      setNumClusters(value);
    } else if (e.target.value === '') {
      setNumClusters(''); // Allow empty input temporarily
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is organizing all the data into neat clusters for you, Senpai! Waku waku!~ ☆
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center p-4 border border-red-500 rounded-lg">
        Oh no! {error}
      </div>
    );
  }

  if (!clusteredData || !clusteredData.clustered_documents || Object.keys(clusteredData.clustered_documents).length === 0) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... No clustered data found to visualize. (T_T) Please ensure data is ingested.
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen flex flex-col">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Mushi's 3D Data Clusters! (ﾉ´ヮ´)ﾉ*:･ﾟ✧
      </h2>

      <div className="max-w-md mx-auto mb-8 p-4 bg-gray-800 rounded-lg shadow-lg flex items-center gap-4">
        <label htmlFor="numClusters" className="text-gray-300 font-medium">Number of Clusters:</label>
        <input
          id="numClusters"
          type="number"
          min="1"
          value={numClusters}
          onChange={handleNumClustersChange}
          className="w-24 p-2 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          aria-label="Number of clusters"
        />
      </div>

      <div
        ref={mountRef}
        className="flex-grow bg-gray-800 rounded-lg shadow-lg overflow-hidden"
        style={{ minHeight: '600px', width: '100%' }} // Ensure the canvas has space
      >
        {/* Three.js scene will be rendered inside this div */}
      </div>

      <div className="mt-8 text-center text-gray-400">
        <p>Senpai, you can drag to rotate the 3D view and scroll to zoom! </p>
        <p>Currently, clusters are randomly positioned for visibility. For true cluster visualization, you'd use the actual embedding vectors to determine their positions in 3D space, which would involve dimensionality reduction (e.g., PCA, t-SNE) if your embeddings are high-dimensional.</p>
        <p>This is a foundational setup, and Mushi is excited to see what amazing visualizations you'll create!</p>
      </div>
    </div>
  );
}

export default DataClusterViewer;
