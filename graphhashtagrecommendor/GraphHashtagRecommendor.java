/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/*
This files expects to be given a file lines where each line consists the tweet and "time of tweet"
seperated by |","| time format : seconds since epoch
*/
package graphhashtagrecommendor;

import java.io.BufferedReader;
import java.io.Console;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Scanner;
import java.util.StringTokenizer;

/**
 *
 * @author vedratn
 */
public class GraphHashtagRecommendor {
    static ArrayList <TweetPair> fullTweets = new ArrayList<TweetPair>();
    static List<List<String>> tweets = new ArrayList<List<String>>();
    static Map<String, Integer> indexMap = new HashMap<String, Integer>();
    static Map<Integer, String> reverseIndexMap = new HashMap<Integer, String>();
    static Map<String, Integer> IDF = new HashMap<String, Integer>();

    static UndirectedGraph tweetGraph;
    
    
    static float filterThreshold;
    static int bfsThreshold;
    
    static void filterTweets(){
        int N;
        N = fullTweets.size();
        System.out.println(N+" is the size of fulltweets");
        StringTokenizer st;
        for(TweetPair tp:fullTweets){
            st = new StringTokenizer(tp.tweet);
            while (st.hasMoreElements()) {
                String token = st.nextElement().toString().toLowerCase();
                if(IDF.containsKey(token)){
                    IDF.put(token, IDF.get(token)+1);
                }else{
                    IDF.put(token, 1);
                }
            }
        }
        float factor;
        for(TweetPair tp:fullTweets){
            st = new StringTokenizer(tp.tweet);
            List<String>s=new ArrayList<String>();
            while (st.hasMoreElements()) {
                String token = st.nextElement().toString().toLowerCase();
                factor = (float)N/IDF.get(token);
                if(factor >= filterThreshold){
                    s.add(token);
                }else{
                    //System.out.println(token +" is rejectedd because it has factor = "+factor);
                }
            }
            tweets.add(s);
        }
    }
    
    static void insertIntoGraph(){
        int index = 0;
        for(List<String>l:tweets){
            for(String s:l){
                if(!indexMap.containsKey(s)){
                    indexMap.put(s,index);
                    reverseIndexMap.put(index,s);
                    index++;
                }
            }
        }
        int size = indexMap.size();
        tweetGraph=new UndirectedGraph();
        for(int i = 0; i < size; i++){
            tweetGraph.addNode(i);
        }
    }
    
    static void findConnections(){
        int index1, index2;
        for(List<String>l:tweets){
            for(int i = 0; i < l.size(); i++){
                for(int j = i+1; j < l.size(); j++){
                    index1 = indexMap.get(l.get(i));
                    index2 = indexMap.get(l.get(j));
                    if(index1 != index2){
                        if(tweetGraph.edgeExists(index1, index2)){
                            tweetGraph.addWeight(index1, index2);
                        }else{
                            tweetGraph.addEdge(index1, index2);
                        }
                    }
                }
            }
        }
        System.out.println("Intex of Kindle2 is :"+indexMap.get("kindle2"));
        
        tweetGraph.normalize();
        /*
        System.out.println("AAYA");
        for(List<String>l:tweets){
            for(int i = 0; i < l.size(); i++){
                for(int j = i+1; j < l.size(); j++){
                    index1 = indexMap.get(l.get(i));
                    index2 = indexMap.get(l.get(j));
                    String key = Integer.toString(Math.min(index1, index2))+"#"+Integer.toString(Math.max(index1, index2));
                    System.out.println(l.get(i)+":"+l.get(j)+"=>"+tweetGraph.weightGraph.get(key)
                            +":"+tweetGraph.vertexWeight.get(index1)+":"+tweetGraph.vertexWeight.get(index2)
                    );
                }
            }
        }*/
     
    }
    
    static void giveHashTags(String tw){
        tw = tw.replaceAll("\\.", " ");
        StringTokenizer st;
        st = new StringTokenizer(tw);
        HashMap<Integer,Double> myScore = new HashMap<Integer,Double>();
        while (st.hasMoreElements()) {
            String token = st.nextElement().toString().toLowerCase();
            if(indexMap.containsKey(token)){
                System.out.println("token is "+token);
                tweetGraph.scoreTerm(indexMap.get(token),myScore,bfsThreshold);
            }
        }
        System.out.println(myScore.size());
        Double maxScore = -1.0;
        Integer maxIndex = -1;
        for(Map.Entry<Integer,Double>entry:myScore.entrySet()){
            if(entry.getValue() > maxScore){
                maxScore = entry.getValue();
                maxIndex = entry.getKey();
            }
        }
        System.out.println("Most apt hashtag is : "+reverseIndexMap.get(maxIndex));
    }
    
    static void insertTweetsAndFilter() throws FileNotFoundException, IOException{
        Scanner user_input = new Scanner( System.in );
        System.out.println("Name of tweetfile: ");
        String file = user_input.next();
        BufferedReader br = new BufferedReader(new FileReader(file));
        String line;
        String tw; int ti;
        while ((line = br.readLine()) != null) {
            tw = line.split("\",\"")[0].replaceAll("\\.", " ");
            ti = Integer.parseInt(line.split("\",\"")[1]);
            fullTweets.add(new TweetPair(tw,ti));
        }
        br.close();  
        filterTweets();

        
    }
    
    public static void main(String[] args) throws IOException {
        // TODO code application logic here
        filterThreshold = 20;
        bfsThreshold = 2;
        PrintStream out = new PrintStream(new FileOutputStream("output.txt"));
        System.setOut(out);
        insertTweetsAndFilter();
        insertIntoGraph();
        findConnections();
        System.out.print("Enter your name: ");
 
      //  open up standard input
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        String myTweet = null;

        //  read the username from the command-line; need to use try/catch with the
        //  readLine() method
        try {
           myTweet = br.readLine();
        } catch (IOException ioe) {
           System.out.println("IO error trying to read your name!");
           System.exit(1);
        }
        giveHashTags(myTweet);
        
    }
    
    
}
