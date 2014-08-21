package graphhashtagrecommendor;
// File: AdjListsGraph.java

/*****************************************************************************
 * File: UndirectedGraph.java
 * Author: Keith Schwarz (htiek@cs.stanford.edu)
 *
 * A class representing an undirected graph where each edge has an associated 
 * real-valued length.  Internally, the class is represented by an adjacency
 * list where each edges appears twice - once in the forward direction and
 * once in the reverse.  In fact, this implementation was formed by taking
 * a standard adjacency list and then duplicating the logic to ensure each
 * edge appears twice.
 */
import java.util.*; // For HashMap, HashSet

public final class UndirectedGraph implements Iterable<Integer> {
    /* A map from nodes in the graph to sets of outgoing edges.  Each
     * set of edges is represented by a map from edges to doubles.
     */
    double unitWeight;
    public UndirectedGraph(){
        unitWeight = 1.0;
    }
    
    private final Map<Integer, Set<Integer>> mGraph = new HashMap<Integer, Set<Integer>>();
    public final Map<String, Double> weightGraph = new HashMap<String, Double>();
    public final Map<Integer, Double> vertexWeight = new HashMap<Integer, Double>();
    /**
     * Adds a new node to the graph.  If the node already exists, this
     * function is a no-op.
     *
     * @param node The node to add.
     * @return Whether or not the node was added.
     */
    public boolean addNode(Integer node) {
        /* If the node already exists, don't do anything. */
        if (mGraph.containsKey(node))
            return false;

        /* Otherwise, add the node with an empty set of outgoing edges. */
        mGraph.put(node, new HashSet<Integer>());
        return true;
    }

    /**
     * Given a node, returns whether that node exists in the graph.
     *
     * @param Integerhe node in question.
     * @return Whether that node exists in the graph.
     */
    public boolean nodeExists(Integer node) {
        return mGraph.containsKey(node);
    }

    /**
     * Given two nodes, adds an arc of that length between those nodes.  If 
     * either endpoint does not exist in the graph, throws a 
     * NoSuchElementException.
     *
     * @param one The first node.
     * @param two The second node.
     * @throws NoSuchElementException If either the start or destination nodes
     *                                do not exist.
     */
    public void addEdge(Integer one, Integer two) {
        /* Confirm both endpoints exist. */
        if (!mGraph.containsKey(one) || !mGraph.containsKey(two))
            throw new NoSuchElementException("Both nodes must be in the graph.");

        /* Add the edge in both directions. */
        mGraph.get(one).add(two);
        mGraph.get(two).add(one);
        
        // Add unitWeight
        addWeight(one,two);
    }
    
    public void addWeight(Integer one, Integer two){
        if (!mGraph.containsKey(one) || !mGraph.containsKey(two))
            throw new NoSuchElementException("Both nodes must be in the graph.");
        
        int mini = Math.min(one,two);
        int maxi = Math.max(one,two);
        String key = Integer.toString(mini)+"#"+Integer.toString(maxi);
        if(weightGraph.containsKey(key)){
            weightGraph.put(key, weightGraph.get(key)+unitWeight);
        }else{
            weightGraph.put(key, unitWeight);
        }
        if(vertexWeight.containsKey(mini)){
            vertexWeight.put(mini, vertexWeight.get(mini)+unitWeight);
        }else{
            vertexWeight.put(mini, unitWeight);
        }
        if(vertexWeight.containsKey(maxi)){
            vertexWeight.put(maxi, vertexWeight.get(maxi)+unitWeight);
        }else{
            vertexWeight.put(maxi, unitWeight);
        }
//        System.out.println(key+":"+weightGraph.get(key)+":"+vertexWeight.get(mini)+":"+vertexWeight.get(maxi));
    }
    
    public void scoreTerm(Integer nodeNum, HashMap<Integer,Double>score, Integer threshold){
        //System.out.println("Called for "+nodeNum);
        dfs(nodeNum,1.0,score,threshold,0.5);
    }
    
    void dfs(Integer node, Double score,HashMap<Integer,Double>scoreMap,Integer threshold, Double decayFactor ){
        if(threshold <= 0){
            return;
        }else{
            String key;
            Integer mini, maxi;
            //System.out.println(node+" has "+edgesFrom(node).size()+" edges ");
            for(Integer m:edgesFrom(node)){
                mini = Math.min(node,m);
                maxi = Math.max(node,m);
                key = Integer.toString(mini)+"#"+ Integer.toString(maxi);
                if(scoreMap.containsKey(m)){
                    scoreMap.put(m,scoreMap.get(m)+score*weightGraph.get(key)*decayFactor);
                }else{
                    scoreMap.put(m,score*weightGraph.get(key)*decayFactor);
                }
                dfs(m,score*weightGraph.get(key)*decayFactor,scoreMap,threshold-1,decayFactor);
            }
        }
    }
    
    public void normalize(){
        int index1, index2;
        for (Map.Entry<String, Double> entry : weightGraph.entrySet()) {
            String key = entry.getKey();
            index1 =  Integer.parseInt(key.split("#")[0]);
            index2 =  Integer.parseInt(key.split("#")[1]);
            Double sum = vertexWeight.get(index1)+vertexWeight.get(index2);
//            System.out.println(entry.getValue()/sum);
            weightGraph.put(entry.getKey(),entry.getValue()/sum);    
        }
    }
    
    public void removeWeight(Integer one, Integer two){
        if (!mGraph.containsKey(one) || !mGraph.containsKey(two))
            throw new NoSuchElementException("Both nodes must be in the graph.");
        int mini = Math.min(one,two);
        int maxi = Math.max(one,two);
        String key = Integer.toString(mini)+"#"+Integer.toString(maxi);
        weightGraph.put(key, weightGraph.get(key)-unitWeight);
        vertexWeight.put(one, vertexWeight.get(one)-unitWeight);
        vertexWeight.put(two, vertexWeight.get(two)-unitWeight);
    }
    /**
     * Removes the edge between the indicated endpoints from the graph.  If the
     * edge does not exist, this operation is a no-op.  If either endpoint does
     * not exist, this throws a NoSuchElementException.
     *
     * @param one The start node.
     * @param two The destination node.
     * @throws NoSuchElementException If either node is not in the graph.
     */
    public void removeEdge(Integer one, Integer two) {
        /* Confirm both endpoints exist. */
        if (!mGraph.containsKey(one) || !mGraph.containsKey(two))
            throw new NoSuchElementException("Both nodes must be in the graph.");

        /* Remove the edges from both adjacency lists. */
        mGraph.get(one).remove(two);
        mGraph.get(two).remove(one);
        
        // Remove fromo weightGraph
        int mini = Math.min(one,two);
        int maxi = Math.max(one,two);
        String key = Integer.toString(mini)+"#"+Integer.toString(maxi);
        weightGraph.remove(key);
        vertexWeight.remove(one);
        vertexWeight.remove(two);
    }

    /**
     * Given two endpoints, returns whether an edge exists between them.  If
     * either endpoint does not exist in the graph, throws a 
     * NoSuchElementException.
     *
     * @param one The first endpoint.
     * @param two The second endpoint.
     * @return Whether an edge exists between the endpoints.
     * @throws NoSuchElementException If the endpoints are not nodes in the 
     *                                graph.
     */
    public boolean edgeExists(Integer one, Integer two) {
        /* Confirm both endpoints exist. */
        if (!mGraph.containsKey(one) || !mGraph.containsKey(two))
            throw new NoSuchElementException("Both nodes must be in the graph.");     
        
        /* Graph is symmetric, so we can just check either endpoint. */
        return mGraph.get(one).contains(two);
    }

    /**
     * Given a node in the graph, returns an immutable view of the edges
     * leaving that node.
     *
     * @param node The node whose edges should be queried.
     * @return An immutable view of the edges leaving that node.
     * @throws NoSuchElementException If the node does not exist.
     */
    public Set<Integer> edgesFrom(Integer node) {
        /* Check that the node exists. */
        Set<Integer> arcs = mGraph.get(node);
        if (arcs == null)
            throw new NoSuchElementException("Source node does not exist.");

        return Collections.unmodifiableSet(arcs);
    }

    /**
     * Returns whether a given node is contained in the graph.
     *
     * @param The node to test for inclusion.
     * @return Whether that node is contained in the graph.
     */
    public boolean containsNode(Integer node) {
        return mGraph.containsKey(node);
    }

    /**
     * Returns an iterator that can traverse the nodes in the graph.
     *
     * @return An iterator that traverses the nodes in the graph.
     */
    public Iterator<Integer> iterator() {
        return mGraph.keySet().iterator();
    }

    /**
     * Returns the number of nodes in the graph.
     *
     * @return The number of nodes in the graph.
     */
    public int size() {
        return mGraph.size();
    }

    /**
     * Returns whether the graph is empty.
     *
     * @return Whether the graph is empty.
     */
    public boolean isEmpty() {
        return mGraph.isEmpty();
    }

    /**
     * Returns a human-readable representation of the graph.
     *
     * @return A human-readable representation of the graph.
     */
    public String toString() {
        return mGraph.toString();
    }
}